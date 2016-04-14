"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------............
For future programmmers, the fifth group of  files to read to understand the mrv are views files in each of sub folders inside the mrv folder. When a request is sent
to the urls.py files, the urls.py redirect the request to the views.py files. The Views files process request and sometimes send a template back to where the request 
came from. Each of the method within the view files that process request has a variable name request as input parameter. If the method  returns a template, the template is
always loaded into variable name template_name. Other times too, the method just redirect to another view. Also know that, the view files also load methods from other 
files. For example, the view.py inside mrvutils loads tasks.py inside the measuring folder. The task.py file contains methods calculateTotalCarbonStocks(project_id),
parcelCalculate(parcel_id), def plotCalculate(plot_id), getReCalculateCarbons(request),reCalculateTotalCarbonStocks(project_id, aeq_id), reParcelCalculate(parcel_id, aeq_id),
rePlotCalculate(plot_id, aeq_id) for calculating and recalculating carbon stocks for projects, parcel, and plots.


The Sixth groups of files to read  to understand the mrv are the html  files inside the template folders within each of sub folders located within the mrv folder.
The html files contains javascripts. The html files gives the mrv the front end with the controls. The front end talks to either a view or web service through
the main urls.py.  The webservice or the view then talks to the models. The model then communicates with the database.  So in case of any error or debugging, we start with the 
html page which contains the javascript. From there we can locate the urls that handles the page request to the html page, from there we go to the view or the web service that recieves the request from the urls, from there we can locate the database model  that is behind the web service or the view.
.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------............
"""


# DJANGO IMPORTS
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
#from django.views.generic import TemplateView
#, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.contrib.formtools.wizard.views import CookieWizardView
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms.formsets import formset_factory
from django.views.generic.edit import FormMixin


# SAMPLING DESIGN TOOL IMPORTS
from mrvutils.forms import SamplingDesignForm, SamplingDesignStrataFormset, SamplingDesignStratumForm
import math  # .ceil()

# LEAKAGE TOOL IMPORTS
from mrvutils.forms import LeakageEstimationFormStep1, LeakageEstimationFormStep2

# PROJECT EMISSIONS TOOL IMPORTS
from mrvutils.forms import ProjectEmissionsStrataFormset
from ecalc.ipcc import Combustion_Factor

# SHP2CSV IMPORTS
from django.views.decorators.csrf import csrf_exempt
import tempfile
import zipfile
import shapefile  # from: pip install pyshp
import shutil
import os
import json
import urllib


# GIS IMPORTs
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.contrib.gis.utils import LayerMapping
from osgeo import osr  # used for EPSG transformation method

# PYTHON LIBRARY IMPORTS
from xlwt import Workbook, Worksheet, easyxf
from xlrd import open_workbook
from xlutils.copy import copy as copy_workbook

# PROJECT IMPORTS
from mrvutils.funcs import string2float
from mrvutils.forms import SoilXLSUploadForm, BiomassXLSUploadForm
from mrvapi.v1 import VerboseProjectParcelPlotResource, PlotResource
from mrvapi.models import Project, Plot, Tree, Parcel, ProjectBoundary
from allometric.models import EquationRegion, Equation, EquationSpecies
from sampling_design.models import WorldBorder

import StringIO

from measuring.tasks import *
from celery.result import AsyncResult

# API RESOURCES
ApiProjects = VerboseProjectParcelPlotResource()
ApiPlots = PlotResource()

# GLOBALS
## ...shared between soil_xls_download & soil_xls_upload views:
workbook_encoding = "ascii"
soilsheet_name = "Soil Data"
shp2csv_temp_dir_name = "shp2csv"
shape_limit = 300

SAMPLING_DESIGN_FORMS = [("meta", SamplingDesignForm),
                         ("strata", SamplingDesignStrataFormset)]
SAMPLING_DESIGN_TEMPLATES = {"meta": "mrvutils/sampling_design_form.html",
                             "strata": "mrvutils/sampling_design_form_step2.html"}

LEAKAGE_ESTIMATION_FORMS = [("meta", LeakageEstimationFormStep1),
                            ("agriculture", LeakageEstimationFormStep2)]
LEAKAGE_ESTIMATION_TEMPLATES = {"meta": "mrvutils/leakage_estimation_form.html",
                                "agriculture": "mrvutils/leakage_estimation_form.html"}

PROJECT_EMISSIONS_FORMS = [("strata", ProjectEmissionsStrataFormset)]
PROJECT_EMISSIONS_TEMPLATES = {"strata": "mrvutils/project_emissions_form.html"}

WORLD_MAPPING = {
    'fips' : 'FIPS',
    'iso2' : 'ISO2',
    'iso3' : 'ISO3',
    'un' : 'UN',
    'name' : 'NAME',
    'area' : 'AREA',
    'pop2005' : 'POP2005',
    'region' : 'REGION',
    'subregion' : 'SUBREGION',
    'lon' : 'LON',
    'lat' : 'LAT',
    'mpoly' : 'MULTIPOLYGON',
}

class MixinView(View):
    """ 1) disallows un-auth'd users ... """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MixinView, self).dispatch(*args, **kwargs)


class WOYPView(MixinView, TemplateView):
    template_name = 'woyp.html'


from core.views import BulletinContextView
class LeakageEstimationTool(MixinView, CookieWizardView, BulletinContextView):
    # FIXME: in django 1.6, move .as_view([list]) to this attribute:
    # form_list = [list]

    def get_template_names(self):
        return [LEAKAGE_ESTIMATION_TEMPLATES[self.steps.current]]

    def get_form_kwargs(self, step):
        kwargs = super(LeakageEstimationTool, self).get_form_kwargs(self)
        if step == 'meta':  # Override #1) Pass owner object to form for filtering projects
            kwargs['owner'] = self.request.user
        elif step == 'agriculture':  # Override #2) Pass project object from step 1 to step 2 form for filtering strata
            kwargs['instance'] = self.get_cleaned_data_for_step('meta')['project']
        return kwargs

    def done(self, form_list, **kwargs):
        # Parse the data we need
        meta_form = form_list[0].cleaned_data
        agriculture_form = form_list[1].cleaned_data

        area_project = 0
        area_pasture = 0
        delta_carbon_tc = 0
        for stratum in agriculture_form:
            area_project += stratum['area']
            area_pasture += stratum['area_pasture_ha']
            stratum['delta_carbon_tc'] = stratum['area_pasture_ha'] * (stratum['verification_tc_ha'] - stratum['beginning_tc_ha'])
            delta_carbon_tc += stratum['delta_carbon_tc']

        result = float(meta_form['forestland_fraction']) / meta_form['project'].duration * delta_carbon_tc * area_pasture / area_project * 44 / 12

        return render_to_response('mrvutils/leakage_estimation_results.html',
                                  {'meta_form': meta_form,
                                   'agriculture_form': agriculture_form,
                                   'area_pasture': area_pasture,
                                   'area_project': area_project,
                                   'area_fraction': area_pasture / area_project,
                                   'delta_carbon_tc': delta_carbon_tc,
                                   'result': "%.2f" % result},
                                  context_instance=RequestContext(self.request))


class SamplingDesignTool(MixinView, CookieWizardView):
    # FIXME: in django 1.6, move .as_view([list]) to this attribute:
    # form_list = [list]

    T_STATISTICS = {'99%': 2.576,  # FIXME: replace with actual formula?
                    '95%': 1.96,
                    '90%': 1.645}

    def get_template_names(self):
    	#return [SAMPLING_DESIGN_TEMPLATES['strata']]
        return [SAMPLING_DESIGN_TEMPLATES[self.steps.current]]

    # def get_form_initial(self, step):
    #     if step == 'meta':
    #         # project = Project.objects.get(id = self.request.session['project_id'])
    #         # if project.reported_area:
    #         #     return self.initial_dict.get(step, {'project_area_ha': project.reported_area})
    #         return self.initial_dict.get(step, {}) #'project_area_ha': 0
    #     elif step == 'strata':
    #         parcels_query = Parcel.objects.filter(project = self.request.session['project_id']).order_by('name')
    #         parcels = []
    #         for p in parcels_query:
    #             parcels.append({'area_ha': p.area_reported, 'name': p.name, 'mean_tc_ha': None, 'plot_size_ha': None, 'std_dev_tc_ha': None})
    #         return self.initial_dict.get(step, {})

    def get_form_kwargs(self, step):
        kwargs = super(SamplingDesignTool, self).get_form_kwargs(self)
        if step == 'meta':
            kwargs['owner'] = self.request.user
            kwargs['project_id'] = self.request.session['project_id']
        elif step == 'strata':
            #kwargs['instance'] = self.get_cleaned_data_for_step('meta')['project']
        	kwargs['instance'] = Project.objects.get(id = self.request.session['project_id'])
        return kwargs

    def done(self, form_list, **kwargs):
        # Parse the data we need
        meta_form = form_list[0].cleaned_data
        strata_form = form_list[1].cleaned_data

        # Intermediate calculations
        intermediate = meta_form  # copy dict initially
        strata_intermediate = list()
        intermediate['project_area_ha'] = 0
        for stratum in strata_form:
            intermediate['project_area_ha'] += stratum['area_reported']
        for stratum in strata_form:
            stratum_intermediate = stratum  # copy dict initially
            # then perform intermediate calculations
            try:
                stratum_intermediate['variance'] = stratum_intermediate['std_dev_tc_ha'] ** 2
                stratum_intermediate['variance_coefficient'] = stratum['std_dev_tc_ha'] / stratum['mean_tc_ha']
                stratum_intermediate['N'] = stratum['area_ha'] / stratum['plot_size_ha']
                stratum_intermediate['area_ratio'] = stratum_intermediate['area_reported'] / intermediate['project_area_ha']  # for use in calculating weighted figures
            except ZeroDivisonError:
                messages.add_message(request, messages.ERROR, "Divide by zero error")
                return HttpResponseRedirect(reverse('sampling-design-tool'))
            # LULUCF
            stratum_intermediate['Ns'] = stratum_intermediate['N'] * stratum_intermediate['std_dev_tc_ha']  # N*s
            stratum_intermediate['Ns2'] = stratum_intermediate['N'] * stratum_intermediate['variance']  # N*s^2
            strata_intermediate.append(stratum_intermediate)
        intermediate['sum_N'] = reduce(lambda a, x: a + x['N'], strata_intermediate, 0)
        intermediate['sum_Ns'] = reduce(lambda a, x: a + x['Ns'], strata_intermediate, 0)
        intermediate['sum_Ns2'] = reduce(lambda a, x: a + x['Ns2'], strata_intermediate, 0)
        intermediate['sum_area_ha'] = reduce(lambda a, x: a + x['area_reported'], strata_intermediate, 0)
        intermediate['weighted_mean_tc_ha'] = reduce(lambda a, x: a + x['mean_tc_ha'] * x['area_ratio'], strata_intermediate, 0)
        intermediate['weighted_plot_size_ha'] = reduce(lambda a, x: a + x['plot_size_ha'] * x['area_ratio'], strata_intermediate, 0)
        intermediate['weighted_std_dev_tc_ha'] = reduce(lambda a, x: a + x['std_dev_tc_ha'] * x['area_ratio'], strata_intermediate, 0)
        intermediate['weighted_total_variance'] = reduce(lambda a, x: a + x['variance'] * x['area_ratio'], strata_intermediate, 0)
        intermediate['t'] = self.T_STATISTICS[meta_form['confidence_level']]  # t-statistic at df = infinity, 95% confidence level
        # LULUCF
        intermediate['E'] = intermediate['weighted_mean_tc_ha'] * float(intermediate['level_of_error'])  # "allowable error"

        # Results calculation
        project_n_plots = (intermediate['sum_Ns'] ** 2) \
            / ((intermediate['sum_N'] * intermediate['E'] / intermediate['t']) ** 2 + intermediate['sum_Ns2'])
        results = dict()
        for stratum in strata_intermediate:
            stratum['n_plots'] = math.ceil(project_n_plots * stratum['Ns'] / intermediate['sum_Ns'])
        results['total_n_plots'] = "%i" % reduce(lambda a, x: a + x['n_plots'], strata_intermediate, 0)

        # Additional string formatting not done elsewhere (for use in templated response)
        for stratum in strata_intermediate:
            for k, v in stratum.items():
                if k in ['name', 'n_plots']:
                    continue  # because we format these attributes elsewhere
                stratum[k] = "%.2f" % v
            stratum['n_plots'] = "%i" % stratum['n_plots']

        # Add final strata container to results context
        results['strata'] = strata_intermediate

        return render_to_response('mrvutils/sampling_design_results.html',
                                  {'meta_form': meta_form,
                                   'strata_form': strata_form,
                                   'intermediate': intermediate,
                                   'results': results,
                                   'mathjax': settings.MATHJAX_CDN_URL},
                                  context_instance=RequestContext(self.request))




class ProjectEmissionsTool(MixinView, CookieWizardView):
    # FIXME: in django 1.6, move .as_view([list]) to this attribute:
    # form_list = [list]

    def get_template_names(self):
        return [PROJECT_EMISSIONS_TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        # Parse the data we need
        strata_form = form_list[0].cleaned_data

        # Intermediate calculations
        intermediate = dict()
        intermediate['CH4_gwp'] = 21
        intermediate['N2O_gwp'] = 310

        strata_intermediate = list()
        for stratum in strata_form:
            stratum_intermediate = stratum  # copy dict initially
            # then perform intermediate calculations
            stratum_intermediate['agb_tdm_burned'] = stratum['area_burned_ha'] * stratum['mean_agb_tdm_ha']
            CF = Combustion_Factor.objects.get(biome=stratum['biome'])
            stratum_intermediate['combustion_factor'] = CF.pctReleased
            stratum_intermediate['CH4_emissions_factor'] = CF.emissCH4
            stratum_intermediate['N2O_emissions_factor'] = CF.emissN2O
            stratum_intermediate['partial_emissions'] = .001 * stratum_intermediate['agb_tdm_burned'] \
                * stratum_intermediate['combustion_factor'] \
                * (stratum_intermediate['CH4_emissions_factor'] * intermediate['CH4_gwp']
                   + stratum_intermediate['N2O_emissions_factor'] * intermediate['N2O_gwp'])

            strata_intermediate.append(stratum_intermediate)

        intermediate['sum_area_burned_ha'] = reduce(lambda a, x: a + x['area_burned_ha'], strata_intermediate, 0)
        intermediate['sum_agb_tdm_burned'] = reduce(lambda a, x: a + x['agb_tdm_burned'], strata_intermediate, 0)

        # Results calculation
        result = reduce(lambda a, x: a + x['partial_emissions'], strata_intermediate, 0)

        # Additional string formatting not done elsewhere (for use in templated response)
        for stratum in strata_intermediate:
            for k, v in stratum.items():
                if k in ['name', 'biome']:
                    continue  # because we format these attributes elsewhere
                stratum[k] = "%.2f" % v

        return render_to_response('mrvutils/project_emissions_results.html',
                                  {'strata_form': strata_form,
                                   'intermediate': intermediate,
                                   'strata_intermediate': strata_intermediate,
                                   'result': "%.2f" % result},
                                  context_instance=RequestContext(self.request))





def shp2csv(request, project_id, polygon_type, debug=False):
    #try:
        # Create return object
    selected =  int( request.POST['iMapReported'])
   
    print selected

    csv_string = ""
    project = Project.objects.get(id=project_id)
    # Retrieve request vars
    try:
        uploaded_file_path = request.FILES["uploaded_file_path"]
    except:
        messages.add_message(request, messages.ERROR, "You must enter a file to be uploaded.")
        return HttpResponseRedirect(reverse('mapping-index', kwargs={'pk':project_id}))
    name_field = request.POST["name_field"]
    #if request.POST["is_plot"] == "true":
    #    pass

    # Determine location to extract zip files
    dummy = tempfile.NamedTemporaryFile(delete=True, prefix='shp2csv_')
    temporary_directory = dummy.name + os.sep  # add the OS-dependent trailing slash "sep"erator
    dummy.close()  # The file is deleted on close so we have a directory handle to use later

    # Open and extract uploaded zip file already saved to server
    archive = zipfile.ZipFile(uploaded_file_path)
    archive.extractall(temporary_directory)

    # Find the .shp file and .prj if it exists
    myshp = None
    myprj = None
    for (root, dirs, files) in os.walk(temporary_directory):
        for file in files:
            if file.lower().endswith('.shp'):
                myshp = os.path.join(root, file)
                #lm = LayerMapping(WorldBorder, myshp, WORLD_MAPPING, transform=False, encoding='iso-8859-1')
                #lm.save(strict=True, verbose=verbose)

            elif file.lower().endswith('.prj'):
                myprj = os.path.join(root, file)

    if not myshp:
        messages.add_message(request, messages.ERROR, "Zip archive does not contain a SHP file")
        return HttpResponseRedirect(reverse('mapping-index', kwargs={'pk':project_id}))


    # Try to parse UTM/EPSG zone from PRJ file, else we raise error
    epsg_zone = None
    if myprj:
        # following adapted from http://gis.stackexchange.com/a/7615
        prj = open(myprj, 'r')
        wkt_definition = prj.read()
        prj.close()
        srs = osr.SpatialReference()
        srs.ImportFromESRI([wkt_definition])
        srs.AutoIdentifyEPSG()
        epsg_zone = srs.GetAuthorityCode(None)
        # important: this epsg_zone is a string; later, the Point() defintion for shapefile points REQUIRES an integer or silently no-ops
        # and later raises an exception upon calling point.transform(...)

        if not epsg_zone:
            shutil.rmtree(temporary_directory)
            messages.add_message(request, messages.ERROR, "The EPSG projection zone could not be parsed correctly. Please try re-projecting (possibly to WGS 84 lat/long).")
            return HttpResponseRedirect(reverse('mapping-index', kwargs={'pk':project_id}))
        elif epsg_zone == '4326':  # This is the EPSG code for WGS 84, which we default to if there is no PRJ file, so let's spare some work by not transforming
            epsg_zone = None

    # Create shape file object
    sf = shapefile.Reader(myshp)

    # Determine index of field argument
    fields = sf.fields
    field_dict = dict()
    for i in range(len(fields)):
        field_dict[fields[i][0]] = i
    field_index = field_dict.get(name_field)

    # Extract points from shape file
    shapeRecs = sf.shapeRecords()
    csv_string = ''
    for i in range(len(shapeRecs)):
        if i >= shape_limit:
            continue
        shape = shapeRecs[i].shape
        record = shapeRecs[i].record
        try:
            label = str(record[field_index - 1])
            if ''.join(label.split()) == "":  # Test if label is blank, and replace if so
                label = "BLANK [ID #%i]" % i
        except:
            label = "NULL [ID #%i]" % i  # Test if record lookup is null
        csv_string += "%s," % label
        if epsg_zone:  # ..then we need to convert from its projection to wgs 84 lat/lng first
            # Convert to geodjango point objects
            wgs84_coordinate_system = SpatialReference(4326)
            shapefile_coordinate_system = SpatialReference(epsg_zone)
            coordinate_system_transformer = CoordTransform(shapefile_coordinate_system, wgs84_coordinate_system)

            shapefile_points = map(lambda x: Point(x[0], x[1], srid=int(epsg_zone)), shape.points)
            map(lambda x: x.transform(coordinate_system_transformer), shapefile_points)  # They are changed in place, so no = definition
            wgs84_point_tuples = map(lambda x: (x.coords[0], x.coords[1]), shapefile_points)
        else:  # .. we assume they're already in lat/lng
            wgs84_point_tuples = shape.points

        # HACK: SOMEWHERE I inverted lat and lng, so note that I flip them back in next one. FIXME - should identify where I screwed up above.
        wgs84_point_tuples = map(lambda x: (x[1], x[0]), wgs84_point_tuples)  # HACK
        # ENDHACK

        string_points = map(lambda x: "%f,%f" % (x[0], x[1]), wgs84_point_tuples)  # Convert from (flt,flt) tuple to "%f,%f" string
        csv_string += reduce(lambda point1, point2: "%s,%s" % (point1, point2), string_points)
        csv_string += ";"




    # Delete files
    del sf  # have to manually delete shapefile here as it has a lock on temp files otherwise
    shutil.rmtree(temporary_directory)

    temp = csv_string.split(';');
    for line in temp:
        line.strip('\r')
        line.strip('\n')
        line.strip(' ')
        if line == '' or line == ' ':
            continue
        line = line.split(',')        
        isPoint = 0
        coordinates2 = []
        if len(line)==3:
           coordinates2.append(float(line[1]))
           coordinates2.append(float(line[2]))
           isPoint = 1
        name = line[0]
        coordinates = []
        i = 2
        for i in range(2,len(line),2):
            coordinates.append((float(line[i]), float(line[i-1])))

        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])
        if polygon_type == 'project':
            if isPoint == 1:
               if selected ==1:
                   pnt = Point(coordinates2[1], coordinates2[0])
                   poly = Polygon([pnt, pnt, pnt, pnt])
                   p = ProjectBoundary(project=project, name = name, poly_mapped = poly, poly_reported = poly)
                   p.save()
               else:
                   pnt = Point(coordinates2[1], coordinates2[0])
                   poly = Polygon([pnt, pnt, pnt, pnt])
                   p = ProjectBoundary(project=project, name = name, poly_mapped = poly)
                   p.save()
            else:
               if selected ==1:
                   poly = Polygon(coordinates)
                   p = ProjectBoundary(project=project, name = name, poly_mapped = poly, poly_reported = poly)
                   p.save()
               else:
                   poly = Polygon(coordinates)
                   p = ProjectBoundary(project=project, name = name, poly_mapped = poly)
                   p.save()
        elif polygon_type == 'parcel':
            if isPoint == 1:
               if selected ==1:
                   pnt = Point(coordinates2[1], coordinates2[0])
                   poly = Polygon([pnt, pnt, pnt, pnt])
                   p = Parcel(project=project, name=name, poly_mapped = poly, poly_reported = poly)
                   p.save()
               else:
                   pnt = Point(coordinates2[1], coordinates2[0])
                   poly = Polygon([pnt, pnt, pnt, pnt])
                   p = Parcel(project=project, name=name, poly_mapped = poly)
                   p.save()
            else:
                if selected ==1:
                     poly = Polygon(coordinates)
                     p = Parcel(project=project, name=name, poly_mapped = poly, poly_reported = poly)
                     p.save()
                else:
                     poly = Polygon(coordinates)
                     p = Parcel(project=project, name=name, poly_mapped = poly)
                     p.save()
        else:
            if isPoint == 1:
                if selected ==1:
                    pnt = Point(coordinates2[1], coordinates2[0])
                    pnt = Polygon([pnt, pnt, pnt, pnt])
                    p = Plot(project=project, name=name, poly_mapped=pnt, poly_reported=pnt)
                    p.save()
                else:
                    pnt = Point(coordinates2[1], coordinates2[0])
                    pnt = Polygon([pnt, pnt, pnt, pnt])
                    p = Plot(project=project, name=name, poly_mapped=pnt)
                    p.save()
            else:
                if selected ==1:
                     pnt = Polygon(coordinates)                     
                     p = Plot(project=project, name=name, poly_mapped=pnt, poly_reported=pnt)
                     pnt.transform(3410)  
                     p.area_reported = pnt.area                                  
                     p.save()
                else:                
                     pnt = Polygon(coordinates)
                     p = Plot(project=project, name=name, poly_mapped=pnt)
                     p.save()




    #lm = LayerMapping(WorldBorder, myshp, WORLD_MAPPING, transform=False, encoding='iso-8859-1')
    #lm.save(strict=True, verbose=verbose)


    # Optionally, write debug output
    if debug:
        temp_debug_file = open(temp_csv_file.name + "_debug.txt", 'a')
        temp_debug_file.write(str(epsg_zone))
        temp_debug_file.close()

    return HttpResponseRedirect(reverse('mapping-index', kwargs={'pk':project_id})) # temp_csv_file.name

    #except Exception as ex:
    #    sridset = set()
     #   for point in shapefile_points:
      #      sridset.add(point.srid)
     #   return HttpResponse("error|%s + [EPSG=%s] [CoordTransform=%s] [SRID Set=%s]" % (str(ex), epsg_zone, str(coordinate_system_transformer), str(sridset)))


def soil_xls_download(request, project_id):
    # Step 0- get project object from API (which applies authorization limits)
    # project = ApiProjects.obj_get(request,pk=project_id)
    # THIS WAS BROKEN WITH TASTYPIE 0.9.12 -- replacing temporarily
    project = Project.objects.get(id=project_id)

    # Step 1- Generate file handle based on project name
    handle = "%s_soil-data.xls" % project.name

    # Step 2- Generate Response & header
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=\"%s\"' % handle

    # Step 3- Generate Excel XLS file and load instructions worksheet
    ## Open instructions template
    module_dir = os.path.dirname(__file__)
    template_path = os.path.join(module_dir, 'resources/soc_template.xls')
    template = open_workbook(template_path, formatting_info=True)
    newbook = copy_workbook(template)

    # Step 4- Generate Excel data input worksheet
    ## Create Soil Sheet
    soilsheet = newbook.add_sheet(soilsheet_name)
    soilsheet.protect = True
    soilsheet.password = "Random1Pas5swordToAv4oidPilo3tErro2rOk1ay?"
    soilsheet.portrait = False
    soilsheet.fit_num_pages = 1
    soilsheet.fit_height_to_pages = 0
    soilsheet.fit_width_to_pages = 1
    ### Create Cell Styles
    heading = easyxf("pattern: pattern solid, fore_color gray25; font: bold on; align: wrap on, vert top; borders: top medium, bottom medium, left medium, right medium;")
    metaheading = easyxf("font: bold on; align: horiz right;")
    editable = easyxf("pattern: pattern solid, fore_color light_yellow; protection: cell_locked false; borders: top medium, bottom medium, left medium, right medium;")
    editablefloat = easyxf("pattern: pattern solid, fore_color light_yellow; protection: cell_locked false; borders: top medium, bottom medium, left medium, right medium;", "#,##0.000")
    reqeditablefloat = easyxf("pattern: pattern solid, fore_color gold; protection: cell_locked false; borders: top medium, bottom medium, left medium, right medium;", "#,##0.000")
    reqeditablepercent = easyxf("pattern: pattern solid, fore_color gold; protection: cell_locked false; borders: top medium, bottom medium, left medium, right medium;", "0.000%")
    immutable = easyxf("borders: top medium, bottom medium, left medium, right medium;")
    typestyle = easyxf("borders: top medium, bottom medium, left medium, right medium;")
    disabled = easyxf("font: italic on; pattern: pattern solid, fore_color gray50; borders: top medium, bottom medium, left medium, right medium;")
    idstyle = easyxf("", ";;;")
    ### Set Col Widths
    soilsheet.col(0).width = 256 * 7
    soilsheet.col(1).width = 256 * 18
    soilsheet.col(2).width = 256 * 18
    soilsheet.col(3).width = 256 * 10
    soilsheet.col(4).width = 256 * 8
    soilsheet.col(5).width = 256 * 8
    soilsheet.col(6).width = 256 * 8
    soilsheet.col(7).width = 256 * 8
    soilsheet.col(8).width = 256 * 8
    soilsheet.col(9).width = 256 * 8
    soilsheet.col(10).width = 256 * 8
    soilsheet.col(11).width = 256 * 8
    soilsheet.col(12).width = 256 * 8
    soilsheet.col(13).width = 256 * 8
    soilsheet.col(14).width = 256 * 8
    soilsheet.col(15).width = 256 * 8
    soilsheet.col(16).width = 256 * 8
    soilsheet.col(17).width = 256 * 8
    soilsheet.col(18).width = 256 * 8
    soilsheet.col(19).width = 256 * 8
    soilsheet.col(20).width = 256 * 8
    ### Write Project Info
    soilsheet.write(0, 0, project.id, idstyle)
    soilsheet.write(0, 1, "Project Name:", metaheading)
    soilsheet.write(0, 2, project.name, immutable)
    soilsheet.write(1, 1, "Project Owner:", metaheading)
    soilsheet.write(1, 2, project.owner.username, immutable)
    soilsheet.write(2, 1, "Project Location:", metaheading)
    soilsheet.write(2, 2, str(project.country) + ", " + str(project.region), immutable)
    ### Write Plot Table Headings
    #soilsheet.write(4, 0, "Plot ID", heading)
    soilsheet.write(4, 1, "Parcel Name", heading)
    soilsheet.write(4, 2, "Plot Name", heading)
    soilsheet.write(4, 3, "Gold Data Exists in DB", heading)
    soilsheet.write(4, 4, "Sample Serial #", heading)
    soilsheet.write(4, 5, "Date", heading)
    soilsheet.write(4, 6, "Start Time", heading)
    soilsheet.write(4, 7, "End Time", heading)
    soilsheet.write(4, 8, "Crew", heading)
    soilsheet.write(4, 9, "Carbon Concentration (%)", heading)
    soilsheet.write(4, 10, "Soil Depth (cm)", heading)
    soilsheet.write(4, 11, "Mass of total air-dried cumulative mass soil sample (g)", heading)
    soilsheet.write(4, 12, "Mass of air-dried cumulative mass coarse fragments (g)", heading)
    soilsheet.write(4, 13, "Mass of air-dried cumulative mass subsample + tin weight (g)", heading)
    soilsheet.write(4, 14, "Mass of oven-dried cumulative mass subsample (g)", heading)
    soilsheet.write(4, 15, "Mass of tin (g)", heading)
    soilsheet.write(4, 16, "Gravimetric moisture content", heading)
    soilsheet.write(4, 17, "Mass of total oven-dried cumulative mass soil sample (g)", heading)
    soilsheet.write(4, 18, "Volume of soil (cm3)", heading)
    soilsheet.write(4, 19, "Bulk density (g cm3)", heading)
    soilsheet.write(4, 20, "Coarse fragments (%)", heading)
    ### Write Plot Table Rows
    row = 5
    for parcel in project.parcel_set.all():
        for plot in parcel.plot_set.all():
            soilsheet.write(row, 0, plot.id, idstyle)
            soilsheet.write(row, 1, plot.parcel.name, immutable)
            soilsheet.write(row, 2, plot.name, immutable)
            soilsheet.write(row, 3, plot.has_soil_data, disabled)
            soilsheet.write(row, 4, plot.soil_serial_number, editable)
            soilsheet.write(row, 5, plot.soil_date, editable)
            soilsheet.write(row, 6, plot.soil_start_time, editable)
            soilsheet.write(row, 7, plot.soil_end_time, editable)
            soilsheet.write(row, 8, plot.soil_crew, editable)
            soilsheet.write(row, 9, plot.soil_carbon_concentration, reqeditablepercent)
            soilsheet.write(row, 10, plot.soil_depth, reqeditablefloat)
            soilsheet.write(row, 11, plot.soil_mass_air_sample, editablefloat)
            soilsheet.write(row, 12, plot.soil_mass_air_sample_coarse_fragments, editablefloat)
            soilsheet.write(row, 13, plot.soil_mass_air_subsample_plus_tin, editablefloat)
            soilsheet.write(row, 14, plot.soil_mass_oven_subsample, editablefloat)
            soilsheet.write(row, 15, plot.soil_mass_tin, editablefloat)
            soilsheet.write(row, 16, plot.soil_gravimetric_moisture_content, editablefloat)
            soilsheet.write(row, 17, plot.soil_mass_oven_sample, editablefloat)
            soilsheet.write(row, 18, plot.soil_volume, editablefloat)
            soilsheet.write(row, 19, plot.soil_bulk_density, reqeditablefloat)
            soilsheet.write(row, 20, plot.soil_coarse_fragments_ratio, reqeditablepercent)
            row += 1

    # Step 5 - Save workbook to response
    newbook.save(response)

    # Step 6- Return resposne
    return response

### This method handles the process of uploading csv files
### for the creation of mapping polygons.
###
### Arguments:
###         request - The request object
###         project_id - The id of the project to save to
###         type - Whether this is a project, parcel, or plot.
def polygonUpload(request, project_id, polygon_type):
    project = Project.objects.get(id=project_id)
    try:
        csvFile = request.FILES['coordinates']
    except:
        messages.add_message(request, messages.ERROR, "Unable to open file")
        return HttpResponseRedirect(reverse('mapping-index', kwargs={'pk':project_id}))

    try:
        csvContent = csvFile.read()
    except:
        messages.add_message(request, messages.ERROR, "Unable to read csv file")
        return HttpResponseRedirect(reverse('mapping-index', kwargs={'pk':project_id}))
    csvContent = csvContent.split('\n')

    if polygon_type == 'plot':
        for line in csvContent:
            polygon_coordinates = line.split(',')
            name = polygon_coordinates[0]
            polygon_coordinates[1] = polygon_coordinates[1].strip('\r')
            t = polygon_coordinates[1][1:len(polygon_coordinates[1]) - 1].split(' ')
            polygon_coordinates[1] = (float(t[0]), float(t[1]))

            new_coordinates = []
            for i in range(0,4):
                new_coordinates.append(polygon_coordinates[1])

            p = Polygon(new_coordinates)

            plot = Plot(project=project, name=name, poly_mapped=p, area_mapped=p.area)
            plot.save()
    else:
        for line in csvContent:
            polygon_coordinates = line.split(',')
            name = polygon_coordinates[0]

            if polygon_coordinates[1] != polygon_coordinates[-1]:
                polygon_coordinates.append(polygon_coordinates[1]);

            for i in range(1,len(polygon_coordinates)):
                polygon_coordinates[i] = polygon_coordinates[i].strip('\r')
                t = polygon_coordinates[i][1:len(polygon_coordinates[i]) - 1].split(' ')
                polygon_coordinates[i] = (float(t[0]), float(t[1]))

            test = polygon_coordinates[1:]

            p = Polygon(polygon_coordinates[1:])
            if polygon_type == 'project':
                project_boundary = ProjectBoundary(project=project, name=name, poly_mapped = p, area_mapped = p.area)
                project_boundary.save()
            elif polygon_type == 'parcel':
                parcel = Parcel(project=project, name=name, poly_mapped = p, area_mapped = p.area)
                parcel.save()

    return HttpResponseRedirect(reverse('mapping-index', kwargs={'pk':project_id}))


def soil_xls_upload(request, project_id):
    if request.method == 'POST':
        try:
            # Step 0- get project object from API (which applies authorization limits)
            #project = ApiProjects.obj_get(request,pk=project_id)  BROKEN WITH TASTYPIE 0.9.12
            project = Project.objects.get(id=project_id)

            # Step 1- Validate form
            form = SoilXLSUploadForm(request.POST, request.FILES)
            if not form.is_valid():
                raise IOError

            # Step 2- Load workbook object
            uploaded_file = request.FILES['workbook']
            workbook = open_workbook(file_contents=uploaded_file.read(), encoding_override=workbook_encoding)
            soilsheet = workbook.sheet_by_name(soilsheet_name)

            # Step 3- Confirm this is the same workbook this mrvutils pre-populated and not anything malicious
            #return HttpResponse(str(int(soilsheet.cell(0, 0).value)) + "<br>" + str(int(project_id)) + "<br>" + int(soilsheet.cell(0, 0).value) + "<br>" + int(project_id))
            if int(soilsheet.cell(0, 0).value) != int(project_id):
                return HttpResponse("This upload sheet is not associated with this project. Contact GOES for assistance.")

            # Step 4- Read-write values from worksheet
            for rindex in range(5, soilsheet.nrows):  # rindex=5 is the first plot row in pre-pop soilsheet
                # Retrieve plot object from API
                plot_id = soilsheet.cell(rindex, 0).value
                #plot = ApiPlots.obj_get(request, pk=plot_id) BROKEN WITH TASTYPIE 0.9.12
                plot = Plot.objects.get(id=plot_id)  # FIXME: add a fallback to match id using name if the id has changed (in case where user deletes then reuploads)
                # Update plot object with values from spreadsheet
                plot.soil_serial_number = soilsheet.cell(rindex, 4).value
                plot.soil_date = soilsheet.cell(rindex, 5).value
                plot.soil_start_time = soilsheet.cell(rindex, 6).value
                plot.soil_end_time = soilsheet.cell(rindex, 7).value
                plot.soil_crew = soilsheet.cell(rindex, 8).value
                plot.soil_carbon_concentration = string2float(soilsheet.cell(rindex, 9).value)
                plot.soil_depth = string2float(soilsheet.cell(rindex, 10).value)
                plot.soil_mass_air_sample = string2float(soilsheet.cell(rindex, 11).value)
                plot.soil_mass_air_sample_coarse_fragments = string2float(soilsheet.cell(rindex, 12).value)
                plot.soil_mass_air_subsample_plus_tin = string2float(soilsheet.cell(rindex, 13).value)
                plot.soil_mass_oven_subsample = string2float(soilsheet.cell(rindex, 14).value)
                plot.soil_mass_tin = string2float(soilsheet.cell(rindex, 15).value)
                plot.soil_gravimetric_moisture_content = string2float(soilsheet.cell(rindex, 16).value)
                plot.soil_mass_oven_sample = string2float(soilsheet.cell(rindex, 17).value)
                plot.soil_volume = string2float(soilsheet.cell(rindex, 18).value)
                plot.soil_bulk_density = string2float(soilsheet.cell(rindex, 19).value)
                plot.soil_coarse_fragments_ratio = string2float(soilsheet.cell(rindex, 20).value)
                # Save plot object
                plot.save()
            return HttpResponseRedirect(reverse('data-management', kwargs={'pk':project_id}))
        except Exception as ex:
            return HttpResponse("The soil data upload failed. Please contact GOES with this information:<br><br>Error detail: %s" % ex)
    form = SoilXLSUploadForm()
    return render_to_response('mrvutils/soil_xls_upload.html', {'form': form, 'project_id': project_id}, context_instance=RequestContext(request))

def biomass_xls_upload(request, project_id):
    def any(iterable):
        for element in iterable:
            if element.value:
                return True
        return False

    if request.method == 'POST':
        try:
            try:
                project = Project.objects.get(id=project_id)
            except:
                Exception("Incorrect Project ID")

            # Step 1 - Validate form
            form = BiomassXLSUploadForm(request.POST, request.FILES)

            if not form.is_valid():
                raise IOError

            region_field = form.cleaned_data['region']
            equation_field = form.cleaned_data['equation']

            if region_field < 0 or region_field is None:
                raise Exception(("You have incorrectly set the region %d." % region_field))

            region = None
            equation = None
            if region_field != 0:
                try:
                    region = EquationRegion.objects.get(id = region_field)
                except:
                    raise Exception('No region by that value')

            try:
                equation = Equation.objects.get(id=equation_field)
            except:
                equation = None


            # Step 2 - Load workbook object
            workbook = open_workbook(file_contents=request.FILES['workbook'].read(), encoding_override=workbook_encoding)
            biomassSheet = workbook.sheet_by_name('Plot Data for Upload')

            biomassSheets = []

            #for sheet in workbook.worksheet:
            #    match = re.search(r'^Project Carbon Pool ([0-9]+)$',sheet.title)
            #    if(match):
            #        biomassSheets.append(sheet)

            #return HttpResponse(len(biomassSheets), status=200)



            # Step 3 - Load the Plot Metadata
            if biomassSheet.cell(0,0).value != 'PLOT METADATA' or biomassSheet.cell(33,0).value != 'TREE INVENTORY DATA':
                return HttpResponse("Incorrect Document", status=400)

            if biomassSheet.cell(7,1).value != project.name:
                return HttpResponse("Incorrect Project name", status=400)

            biomassData = {}
            biomassData['project'] = project.id

            parcel_name = biomassSheet.cell(8,1).value

            if not parcel_name:
                raise Exception("No parcel name listed")


            # See if a parcel already exists with this name
            try:
                parcel = Parcel.objects.get(name__iexact=parcel_name, project=project.id)
            except:
                parcel = Parcel()
                parcel.name = parcel_name
                parcel.project = project
                parcel.aeq = equation


            plot_name = biomassSheet.cell(9,1).value
            plot_area = biomassSheet.cell(11,1).value
            if not plot_name:
                raise Exception("No plot name listed")


            try:
                if parcel.id:
                    plot = Plot.objects.get(name = plot_name, parcel=parcel)
                else:
                    raise Exception("Parcel hasn't been created yet")
            except:
                plot = Plot()
                plot.name = plot_name

            plot.region = region

            if region:
                plot.calculate_by_species = True
            plot.aeq = equation
            rootshoot = form.cleaned_data['root_to_shoot']
            plot.root_shoot_ratio = form.cleaned_data['root_to_shoot']
            plot.area_reported = plot_area
            plot.project = project

            shape_reported = biomassSheet.cell(12,1).value
            if not shape_reported:
                raise Exception("Must have a plot shape")

            plot.shape_reported = shape_reported

            if shape_reported == 'rectangular':
                dimensions = biomassSheet.cell(13,1).value
                if not dimensions:
                    raise Exception("You selected Rectangular. Must have dimensions")
                plot.dimensions_reported = dimensions
            elif shape_reported == 'circular':
                radius = biomassSheet.cell(14,1).value
                if not radius:
                    raise Exception("You selected circular. Must have a radius")

                plot.dimensions_reported = radius



            # Do column B of the meta data section
            plot.sample_date = biomassSheet.cell(3,1).value
            plot.sample_start_time = biomassSheet.cell(4,1).value
            plot.sample_end_time = biomassSheet.cell(5,1).value
            plot.sample_crew = biomassSheet.cell(6,1).value
            plot.description = biomassSheet.cell(10,1).value
            plot.gps_latitude = biomassSheet.cell(15,1).value
            plot.gps_longitude = biomassSheet.cell(16,1).value
            plot.elevation = biomassSheet.cell(17,1).value
            plot.slope_condition = biomassSheet.cell(18,1).value
            plot.hemi_photo_center = biomassSheet.cell(19,1).value
            plot.hemi_photo_north = biomassSheet.cell(20,1).value
            plot.hemi_photo_east = biomassSheet.cell(21,1).value
            plot.hemi_photo_south = biomassSheet.cell(22,1).value
            plot.hemi_photo_west = biomassSheet.cell(23,1).value
            plot.horiz_photo_north = biomassSheet.cell(24,1).value
            plot.horiz_photo_east = biomassSheet.cell(25,1).value
            plot.horiz_photo_south = biomassSheet.cell(26,1).value
            plot.horiz_photo_west = biomassSheet.cell(27,1).value
            plot.weather = biomassSheet.cell(28,1).value
            plot.comments = biomassSheet.cell(29,1).value

            # Begin column F of the meta data section
            if biomassSheet.cell(3,5).value:
                plot.litter_tc_ha = biomassSheet.cell(3,5).value
            if biomassSheet.cell(4,5).value:
                plot.deadwood_tc_ha = biomassSheet.cell(4,5).value
            if biomassSheet.cell(5,5).value:
                plot.nontree_agb_tc_ha = biomassSheet.cell(5,5).value
            if biomassSheet.cell(6,5).value:
                plot.nontree_bgb_tc_ha = biomassSheet.cell(6,5).value

            # Do submplot 1 values
            if biomassSheet.cell(9,5).value and not (biomassSheet.cell(14,5).value and biomassSheet.cell(15,5).value):
                raise Exception("Subplot not correctly formatted")

           
            plot.subplot_1_name = biomassSheet.cell(9,5).value
            if biomassSheet.cell(10,5).value:
                plot.subplot_1_area_m2 = biomassSheet.cell(10,5).value                
            if biomassSheet.cell(14,5).value:
                plot.subplot_1_lower_bound = biomassSheet.cell(14,5).value                
            if biomassSheet.cell(15,5).value:
                plot.subplot_1_upper_bound = biomassSheet.cell(15,5).value                
            
            # Do subplot 2 values
            if biomassSheet.cell(17,5).value and not (biomassSheet.cell(22,5).value and biomassSheet.cell(23,5).value):
                raise Exception("Subplot not correctly formatted")

            plot.subplot_2_name = biomassSheet.cell(17,5).value
            if biomassSheet.cell(18,5).value:
                plot.subplot_2_area_m2 = biomassSheet.cell(18,5).value                
            if biomassSheet.cell(22,5).value:
                plot.subplot_2_lower_bound = biomassSheet.cell(22,5).value                
            if biomassSheet.cell(23,5).value:
                plot.subplot_2_upper_bound = biomassSheet.cell(23,5).value               
            
            # Do subplot 3 values
            if biomassSheet.cell(25,5).value and not (biomassSheet.cell(30,5).value and biomassSheet.cell(31,5).value):
                raise Exception("Subplot not correctly formatted")
            plot.subplot_3_name = biomassSheet.cell(25,5).value

            if biomassSheet.cell(26,5).value:
                plot.subplot_3_area_m2 = biomassSheet.cell(26,5).value
            if biomassSheet.cell(30,5).value:
                plot.subplot_3_lower_bound = biomassSheet.cell(30,5).value
            if biomassSheet.cell(31,5).value:
                plot.subplot_3_upper_bound = biomassSheet.cell(31,5).value
            trees = []
            for i in range(36, biomassSheet.nrows):
                v = biomassSheet.row(i)[1:]
                if (not v[0].value or v[0].value == '' or v[0].value == ' ') and v[1].value:
                    if ' ' in v[1].value:
                        s = v[1].value.split(' ')
                        v[0].value = s[0]
                        v[1].value = s[1]
                del v[3]

                if not any(v):
                    break

                if v[2].value is None:
                    raise Exception("DBH is required")

                if len(v) != 8:
                    raise Exception("Improperly formatted sheet")

                t = Tree()
                t.plot = plot
                t.genus = v[0].value
                t.species = v[1].value
                t.dbh = v[2].value
                if v[3].value:
                    t.total_height = v[3].value
                if v[4].value:
                    t.wood_gravity = v[4].value
                if v[5].value:
                    t.crown_d_max = v[5].value
                if v[6].value:
                    t.crown_d_90 = v[6].value
                t.comments = v[7].value
                t.excel_row = biomassSheet.cell(i,0).value
                trees.append(t)
            parcel.save()           
            plot.parcel = parcel
            plot.save()            
            for i in trees:
                i.plot = plot

            Tree.objects.bulk_create(trees)

            plot._update_tree_aeq_association()

        except IOError:
            messages.add_message(request, messages.ERROR, ("You forgot something on the form."))
            return HttpResponseRedirect(('/measuring/data_management/%s/' % project_id))
        except Exception as e:
            messages.add_message(request, messages.ERROR, ("Something went wrong. %s" % e.args))
            return HttpResponseRedirect(('/measuring/data_management/%s/' % project_id))
        except:
            messages.add_message(request, messages.ERROR, "Something went wrong.")
            return HttpResponse(('/measuring/data_management/%s/' % project_id))

    messages.add_message(request, messages.SUCCESS, "Successfully Uploaded Inventory Sheet")    
    calculateTotalCarbonStocks.delay(project.id)   
    return HttpResponseRedirect(('/measuring/data_management/plot_inventory/%s/%s/' % (project_id, plot.id)))
