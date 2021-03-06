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
from django.views.generic import View, TemplateView, FormView, CreateView
from django.core.urlresolvers import reverse
from django.contrib.formtools.wizard.views import CookieWizardView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.contrib import messages

# PROJECT IMPORTS
from sampling_design.forms import *
from mrvapi.models import Project, Parcel, ProjectBoundary, ProjectPermissions

# PYTHON IMPORTS
import math, scipy, scipy.stats, numpy

SAMPLING_DESIGN_FORMS = [("meta", SamplingDesignForm1),
                         ("strata", SamplingDesignStrataFormset)]
SAMPLING_DESIGN_TEMPLATES = {"meta": "sampling_design/sampling_design_form.html",
                             "strata": "sampling_design/sampling_design_form_step_2.html"}

class MixinView(View):
    """ 1) disallows un-auth'd users ... """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MixinView, self).dispatch(*args, **kwargs)


class PlotMappingTool(MixinView, TemplateView):
    template_name = 'sampling_design/plot_mapping_tool.html'


class SamplingDesignTool(MixinView, CookieWizardView):
    # FIXME: in django 1.6, move .as_view([list]) to this attribute:
    # form_list = [list]

    def get_template_names(self):
        return [SAMPLING_DESIGN_TEMPLATES[self.steps.current]]

    def get_context_data(self, **kwargs):
        context = super(SamplingDesignTool, self).get_context_data(**kwargs)

        project = Project.objects.get(id = self.request.session['project_id'])
        project_carbon_stock = Project.objects.get(id=self.request.session['project_id'])
        parcels = project_carbon_stock.parcel_set.all()
        parcel = Parcel.objects.filter(project = self.request.session['project_id']).order_by('name')

        parcel_info = []
        for p in parcel:
            parcel_info.append(p.name + ", " + str(p.area) + ", ")

        # c is a counter/indexer and p is the parcel.
        for c, p in enumerate(parcels):
            # tc_ha_totals 0 and 1 have to be mean_total_tc_ha and std_tc_ha # double check
            parcel_info[c] += str(p.tc_ha_totals[0]) + ", " + str(p.tc_ha_totals[1])
        context['parcels'] = parcel_info

        return context

    def done(self, form_list, **kwargs):
        # Parse the data we need
        meta_form = form_list[0].cleaned_data
        strata_form = form_list[1].cleaned_data

        # Intermediate calculations
        intermediate = meta_form  # copy dict initially
        strata_intermediate = list()
        intermediate['project_area_ha'] = 0
        test = dict()
        test_list = []
        for stratum in strata_form:
            intermediate['project_area_ha'] += stratum['area_reported']
        for stratum in strata_form:
            stratum_intermediate = stratum  # copy dict initially
            # then perform intermediate calculations
            try:
                stratum_intermediate['variance'] = stratum_intermediate['std_total_tc_ha'] ** 2
                stratum_intermediate['variance_coefficient'] = stratum['std_total_tc_ha'] / stratum['mean_total_tc_ha']
                stratum_intermediate['N'] = stratum['area_reported'] / stratum['plot_size_ha']
                stratum_intermediate['area_ratio'] = stratum_intermediate['area_reported'] / intermediate['project_area_ha']  # for use in calculating weighted figures
            except ZeroDivisionError:
                messages.add_message(self.request, messages.ERROR, "You attempted to divide by zero.")
                return HttpResponseRedirect(reverse('sampling-design-tool'))
            # LULUCF
            stratum_intermediate['Ns'] = stratum_intermediate['N'] * stratum_intermediate['std_total_tc_ha']  # N*s
            stratum_intermediate['Ns2'] = stratum_intermediate['N'] * stratum_intermediate['variance']  # N*s^2
            strata_intermediate.append(stratum_intermediate)
        intermediate['sum_N'] = reduce(lambda a, x: a + x['N'], strata_intermediate, 0)
        intermediate['sum_Ns'] = reduce(lambda a, x: a + x['Ns'], strata_intermediate, 0)
        intermediate['sum_Ns2'] = reduce(lambda a, x: a + x['Ns2'], strata_intermediate, 0)
        intermediate['sum_area_ha'] = reduce(lambda a, x: a + x['area_reported'], strata_intermediate, 0)
        intermediate['weighted_mean_tc_ha'] = reduce(lambda a, x: a + x['mean_total_tc_ha'] * x['area_ratio'], strata_intermediate, 0)
        intermediate['weighted_plot_size_ha'] = reduce(lambda a, x: a + x['plot_size_ha'] * x['area_ratio'], strata_intermediate, 0)
        intermediate['weighted_std_dev_tc_ha'] = reduce(lambda a, x: a + x['std_total_tc_ha'] * x['area_ratio'], strata_intermediate, 0)
        intermediate['weighted_total_variance'] = reduce(lambda a, x: a + x['variance'] * x['area_ratio'], strata_intermediate, 0)
        intermediate['t'] = scipy.stats.norm.interval(float(meta_form['confidence_level'].encode('ascii', 'ignore').strip('%'))/100, loc=0, scale=1)[1]
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
        #raise Exception('test')
        return render_to_response('sampling_design/sampling_design_results.html',
                                  {'meta_form': meta_form,
                                   'strata_form': strata_form,
                                   'intermediate': intermediate,
                                   'results': results,
                                   'mathjax': settings.MATHJAX_CDN_URL},
                                  context_instance=RequestContext(self.request))
