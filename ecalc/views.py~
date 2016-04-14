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
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import permalink
from mrvapi.models import Project, ProjectPermissions
from models import LandCover, LandUse, Parcel, Practice, Scenario, CarbonPools
from forms import Project_Form, LandUse_FormSet, ReferenceScenario_Form, ProjectScenario_Form, LandUse_BaseFormSet, ReportWizardScenarioFormset, UpdateProject_form
from utils import UpdatePools
from ipcc import Continent, Climate_Zone, Moisture_Zone, Soil_Type, GWP, Forest_Growth
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView, View


from django.contrib import messages

class PrepopulateMixinView(View):
    def dispatch(self, *args, **kwargs):
        project = Project.objects.get(id=self.request.session["project_id"])
        if project.climate_zone is None or project.moisture_zone is None or project.duration is None:
            messages.add_message(self.request, messages.ERROR, 'You must define soil, moisture, climate, duration before using the emissions calculator.')
            return HttpResponseRedirect('/core/edit_project/%s' % project.pk)
        return super(PrepopulateMixinView, self).dispatch(*args, **kwargs)

# ecalc home
class HomeView(PrepopulateMixinView, TemplateView):
    template_name='ecalc/base.html'
    def get_context_data(self,**kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        if Forest_Growth.objects.count():
            context['setup'] = False
        else: context['setup'] = True
        context['home'] = True
        return context

# report form wizard
from django.contrib.formtools.wizard.views import CookieWizardView
#import pyflot
REPORT_WIZARD_FORMS = [("scenarios", ReportWizardScenarioFormset)]
REPORT_WIZARD_TEMPLATES = {"scenarios": "report_wizard_form.html"}

# report form wizard - tracking tools
from xlutils.copy import copy as copy_workbook
from xlwt import Workbook, Worksheet, easyxf
from xlrd import open_workbook
import os


def changeCell(worksheet, row, col, text):
    """ Changes a worksheet cell text while preserving formatting """
    # Adapted from http://stackoverflow.com/a/7686555/1545769
    previousCell = worksheet._Worksheet__rows.get(row)._Row__cells.get(col)
    worksheet.write(row, col, text)
    newCell = worksheet._Worksheet__rows.get(row)._Row__cells.get(col)
    newCell.xf_idx = previousCell.xf_idx


class ReportWizardView(CookieWizardView):
    # FIXME: in django 1.6, move .as_view([list]) to this attribute:
    # form_list = [list]

    def get_template_names(self):
        return [REPORT_WIZARD_TEMPLATES[self.steps.current]]

    def get_form_kwargs(self, step):
        kwargs = super(ReportWizardView, self).get_form_kwargs(self)
        if step == 'scenarios':  # Override 1) Pass project object to Form constructor for filtering scenario objects
            kwargs['project'] = get_object_or_404(Project, id=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super(ReportWizardView, self).get_context_data(form=form, **kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['pk'])  # Override 1) Pass project object to template
        return context

    def done(self, form_list, **kwargs):
        # Parse the data we need
        parcels_formset = form_list[0].cleaned_data

        scenarios = list()
        for parcel in parcels_formset:
            scenario = parcel.get('scenario', None)
            if scenario:
                scenarios.append(scenario)

        project_cumulative_emissions = reduce(lambda a, x: a + x.EmissionsDifference(), scenarios, 0.0)

        #names = reduce(lambda a, x: "%s %s" % (a, x.name), scenarios, '')

        return render_to_response('report_wizard_results.html',
                                  {'project': get_object_or_404(Project, id=self.kwargs['pk']),
                                   'scenarios': scenarios,
                                   'project_cumulative_emissions': project_cumulative_emissions},
                                  context_instance=RequestContext(self.request))


def ReportWizardGEFTrackingToolCCM(request, **kwargs):
    project_id = kwargs.pop('pk')
    delta_emissions = float(request.GET['delta_emissions']) * -1

    project = get_object_or_404(Project, id=project_id)

    # Step 1- Generate file handle based on project name
    handle = "%s_gef_ccm_tracking_tool.xls" % project.name

    # Step 2- Generate Response & header
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=\"%s\"' % handle

    # Step 3- Generate excel file from template in resources folder
    module_dir = os.path.dirname(__file__)
    template_path = os.path.join(module_dir, 'resources/gef_cc_mitigation_tracking_tool.xls')
    template = open_workbook(template_path, formatting_info=True)
    wb = copy_workbook(template)

    ws = wb.get_sheet(1)

    changeCell(ws, 11, 2, project.name)
    changeCell(ws, 155, 2, delta_emissions)

    # Step 4- Save workbook to response
    wb.save(response)

    return response


def ReportWizardGEFTrackingToolSFM(request, **kwargs):
    project_id = kwargs.pop('pk')
    delta_emissions = float(request.GET['delta_emissions']) * -1

    project = get_object_or_404(Project, id=project_id)

    # Step 1- Generate file handle based on project name
    handle = "%s_gef_sfm_redd_plus_tracking_tool.xls" % project.name

    # Step 2- Generate Response & header
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=\"%s\"' % handle

    # Step 3- Generate excel file from template in resources folder
    module_dir = os.path.dirname(__file__)
    template_path = os.path.join(module_dir, 'resources/gef_sfm_redd_plus_tracking_tool.xls')
    template = open_workbook(template_path, formatting_info=True)
    wb = copy_workbook(template)

    ws = wb.get_sheet(2)

    changeCell(ws, 6, 1, project.name)
    changeCell(ws, 75, 6, delta_emissions)

    # Step 4- Save workbook to response
    wb.save(response)

    return response

def review_project(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Poll.DoesNotExist:
        raise Http404
    return render_to_response('ecalc/project_wizard_step_1.html', {'project':project, 'request':request, 'user':request.user})

class ReviewProject(PrepopulateMixinView, DetailView):
    template_name = 'ecalc/project_wizard_step_1.html'
    model = Project
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewProject, self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        return super(ReviewProject, self).get_context_data(**kwargs)


# Project Views
class ProjectsView(PrepopulateMixinView, ListView):
    template_name = 'ecalc/project_list.html'
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectsView, self).dispatch(*args, **kwargs)
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

class ProjectView(DetailView):
    template_name = 'ecalc/project_detail.html'
    model = Project
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectView, self).dispatch(*args, **kwargs)
    #def get_queryset(self):
    #    self.project = get_object_or_404(Project,id=self.kwargs['pk'])
    def get_queryset(self): #  limit query to only user-owned projects or else other users can see
        return super(ProjectView,self).get_queryset().filter(owner=self.request.user)
        #return Project.objects.filter(user=self.request.user)
        # the preceding line works. the actual line is a more generalized case.
    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context['landcover_list'] = context['project'].landcover_set.all()
        context['parcel_list'] = context['project'].ecalc_parcel_set.all()
        context['practice_list'] = context['project'].practice_set.all()
        context['refscenario_list'] = context['project'].scenario_set.filter(reference_scenario__isnull=True)
        context['projscenario_list'] = context['project'].scenario_set.exclude(reference_scenario__isnull=True)
        #print 'request',self.request.META
        return context

class CreateProjectView(CreateView):
    template_name = 'ecalc/project_form.html'
    model=Project
    form_class=Project_Form
    success_url = '/ecalc/projects/'
    wiz_nexturlname = ''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateProjectView, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()

        

        if self.wiz_nexturlname != '':
            url = reverse(self.wiz_nexturlname, kwargs={'ppk':self.object.id})
        else: url = self.success_url
            #return HttpResponseRedirect(self.object.geturl(Parcel.get_new_urlname()))
        return HttpResponseRedirect(url)

#######################################################################
## DeleteLandcover
## --------------------------------------
##      Delete the landcover from the database and redirect back to 
##      the project details page.
## Param:
##      request
##      pk -- The id of the landcover we are trying to delete
##      ppk -- The id of the project we are working with
## Returns:
##      HttpResponse redirecting the user back to the ecalc project details page
##
def DeleteLandcover(request, pk, ppk):
    model = LandCover.objects.get(id=pk)
    model.delete()
    messages.add_message(request, messages.SUCCESS, "LandCover deleted successfully.")
    return HttpResponseRedirect(reverse('ecalc-project', kwargs={'pk':ppk}))
#######################################################################
## DeletePractice
## --------------------------------------
##      Delete the practice from the database and redirect back to 
##      the project details page.
## Param:
##      request
##      pk -- The id of the practice we are trying to delete
##      ppk -- The id of the project we are working with
## Returns:
##      HttpResponse redirecting the user back to the ecalc project details page
##
def DeletePractice(request, pk, ppk):
    model = Practice.objects.get(id=pk)
    model.delete()
    messages.add_message(request, messages.SUCCESS, "Practice deleted successfully.")
    return HttpResponseRedirect(reverse('ecalc-project', kwargs={'pk':ppk}))

def DeleteParcel(request, pk, ppk):
    try:
        parcel = Parcel.objects.get(id=pk)
    except DoesNotExist:
        messages.add_message(request, messages.ERROR, "Parcel Does Not Exist")
        return HttpResponseRedirect(reverse('ecalc-project', kwargs={'pk':ppk}))
    parcel.delete()
    return HttpResponseRedirect(reverse('ecalc-project', kwargs={'pk':ppk}))

def DeleteScenario(request, pk, ppk):
    try:
        sc = Scenario.objects.get(id=pk)
    except DoesNotExist:
        messages.add_message(request, messages.ERROR, "Scenario does not exist")
        return HttpResponseRedirect(reverse('ecalc-project', kwargs={'pk':ppk}))
    sc.delete()
    return HttpResponseRedirect(reverse('ecalc-project', kwargs={'pk':ppk}))

# def DeleteScenario(request, pk, ppk):
#     model = Practice.objects.get(id=pk)
#     model.delete()
#     messages.add_message(request, messages.SUCCESS, "Practice deleted successfully.")
#     return HttpResponseRedirect(reverse('ecalc-project', kwargs={'pk':ppk}))



class DeleteView_(DeleteView):
    template_name = "ecalc/_confirm_delete.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteView_, self).dispatch(*args, **kwargs)

    def get_queryset(self):  # limit query to only user-owned objects or else other users can see
        if self.model == Project:
            return super(DeleteView_, self).get_queryset().filter(user=self.request.user)
        else:  # if self.model == LandCover or self.model == Practice or self.model == Scenario or self.model == :
            return super(DeleteView_, self).get_queryset().filter(project__owner=self.request.user)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return self.object.get_list_url()


class ListView_(ListView):
    """ Abstract base class for custom views """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListView_, self).dispatch(*args, **kwargs)
    def get_queryset(self):
        self.project = get_object_or_404(Project, id=self.kwargs['ppk'], owner=self.request.user)
        return self.model.objects.filter(project=self.project)
    def get_context_data(self, **kwargs):
        context = super(ListView_, self).get_context_data(**kwargs)
        context['project'] = self.project
        context['model'] = self.model
        try:
            context['newurl'] = reverse(self.model.get_new_urlname(), kwargs={'ppk':self.project.id})
        except:
            pass
        return context   
              
class UpdateView_(UpdateView):
    template_name = "ecalc/_form.html"
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateView_, self).dispatch(*args, **kwargs)
    #def get_queryset(self):
    #    self.project = get_object_or_404(Project,id=self.kwargs['ppk'])
    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.object.get_list_url())
    def get_context_data(self, **kwargs):
        context = super(UpdateView_, self).get_context_data(**kwargs)
        project = get_object_or_404(Project, id=self.kwargs['ppk'], owner=self.request.user)
        context['project'] = project
        context['model'] = self.model
        context['modelid'] = self.kwargs['pk']
        try:
            context['listurl'] = context['project'].geturl(self.model.get_list_urlname())
        except: pass
        #if self.request.POST:
        #    context['form'] = self.form_class(self.request.POST,project=project)
        #else:
        #    context['form'] = self.form_class(self.request.GET)
        return context
    class Meta:
        abstract = True

class UpdateLandcover(UpdateView_):
    template_name = "ecalc/edit_landcover_form.html"
    def form_valid(self, form):
        super(UpdateLandcover, self).form_valid(form)
        return HttpResponse('', status=204)

class UpdatePractice(UpdateView_):
    template_name = "ecalc/edit_practice_form.html"
    def form_valid(self, form):
        super(UpdatePractice, self).form_valid(form)
        return HttpResponse('', status=204)
              
class ParcelUpdateView(UpdateView_):
    template_name = "ecalc/create_parcel_form.html"
    def form_valid(self, form):
        self.object = form.save()
        for scenario in self.object.scenario_set.all():
            UpdatePools(scenario)

        #url222 = self.object.get_list_url()
        #raise Exception("got past update pools")
        return HttpResponseRedirect('/ecalc/project/%s' % self.request.session['project_id'])
        #return HttpResponseRedirect(self.object.get_list_url())

class CreateView_(CreateView):
    template_name = "ecalc/_form.html"
    wiz_nexturlname = ''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateView_, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.project = get_object_or_404(Project, id=self.kwargs['ppk'])
        self.object.save()
        if self.wiz_nexturlname == "":
            url = '/ecalc/project/%s/' % self.object.project.id #.get_success_url()
        else: url = reverse(self.wiz_nexturlname, kwargs={'ppk': self.object.project.id})
        return HttpResponseRedirect(url)
    def get_form_kwargs(self, **kwargs):
        #print 'CreateView_ get_form_kwargs'
        kwargs = super(CreateView_, self).get_form_kwargs(**kwargs)
        # if creating new model, then set project
        if kwargs['instance'] is None:
             project = get_object_or_404(Project, id=self.kwargs['ppk'])
             kwargs['instance'] = self.model(project=project)
        return kwargs
        #kwargs['instance'] = self.model(project)
    def get_context_data(self, **kwargs):
        #print 'CreateView_ get_context_data'
        context = super(CreateView_, self).get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['ppk'], owner=self.request.user)
        context['model'] = self.model
        try:
            context['listurl'] = context['project'].geturl(self.model.get_list_urlname())
        except: pass
        #context['helptext'] = "this is a test"
        #context['newurl_popup'] = reverse(self.model.get_new_urlname(), kwargs={'ppk':self.project.id})
        #instance = self.model(project=context['project'])
        #print 'instance project = ', instance.project
        #if self.request.POST:
        #    context['form'] = self.form_class(self.request.POST, instance=instance)
        #else:
        #    context['form'] = self.form_class(instance=instance)
            #initial={'project':context['project']}
        return context  

# class CreateTempView(CreateView_)
#     template_name = "ecalc/create_project_form.html"

#     def form_valid(self,form):
#         return super(CreateparcelView, self).form_valid(form);

class CreateLandcover(CreateView_):
    template_name = "ecalc/create_landcover_form.html"
    def form_valid(self, form):
        super(CreateLandcover, self).form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, "Landcover Added")
        return HttpResponse('', status=204)

class CreatePractice(CreateView_):
    template_name = "ecalc/create_practice_form.html"
    def form_valid(self, form):
        super(CreatePractice, self).form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, "Practice added successfully")
        return HttpResponse('', status=204)

class CreateViewPopup(CreateView_):
    template_name = "ecalc/_form_popup.html"
    #template_name = "ecalc/_form.html"
    def form_valid(self, form):
        super(CreateViewPopup, self).form_valid(form)
        return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                            (escape(self.object._get_pk_val()), escape(self.object)) )

 
        
class CreateScenarioView(CreateView_):
    template_name = "ecalc/scenario_form.html"
    def form_valid(self,form):
        #print "CreateScenarioView form_valid"
        #super(CreateScenarioView,self).form_valid(form)
        # Before getting context data, ensure forms 
        dat = self.get_context_data()
        #scenario_form = dat['scenario_form']
        landuse_formset = dat['landuse_formset']
        if landuse_formset.is_valid():
            scenario = form.save(commit=False)
            if not scenario.parcel:
                scenario.parcel = scenario.reference_scenario.parcel
            scenario.save();
            luforms = landuse_formset.save(commit=False)
            luforms[0].start_year = 0
            for lu in luforms:
                lu.scenario = scenario
                lu.save()
            #landuse_formset.save()
            #lu.scenario = scenario
            #lu.save()
            UpdatePools(scenario)
            if self.wiz_nexturlname == "":
                if scenario.reference_scenario:
                    url = '/ecalc/project/%s/' % scenario.project.id
                else: url = '/ecalc/project/%s/' % scenario.project.id
            else: url = reverse(self.wiz_nexturlname, kwargs={'ppk':scenario.project.id})
            return HttpResponseRedirect(url)
        else:
            return self.render_to_response(self.get_context_data(form=form))  
    def get_context_data(self,**kwargs):
        #print 'CreateScenarioView get_context_data'
        context = super(CreateScenarioView, self).get_context_data(**kwargs)
        #scenario = Scenario.objects.get(id=self.kwargs['pk'])
        # For new scenarios
        scenario = Scenario(project=context['project'])
        try:
            loc = str(context['form'].__class__).find("Reference")
            if loc != -1:
                context['scprefix'] = 'Reference'
            else: context['scprefix'] = 'Project'
        except:
            context['scprefix'] = 'Project'
        context['scenario'] = scenario
        context['listurl'] = context['project'].get_absolute_url #geturl(self.model.get_list_urlname())
        project_id = context['project'].id
        #LandUse = LandUse(scenario=scenario)
        if self.request.POST:
            #context['form'] = Scenario_Form(self.request.POST, instance=scenario)
            context['landuse_formset'] = LandUse_FormSet(self.request.POST, instance=scenario, prefix=project_id)
            context['landuse_formset'].full_clean()
        else:
            #context['form'] = Scenario_Form(instance=scenario)
            context['landuse_formset'] = LandUse_FormSet(prefix=project_id, instance=scenario)
        return context            


class UpdateScenarioView(UpdateView_):
    template_name = "ecalc/scenario_form.html"
    def form_valid(self,form):
        dat = self.get_context_data()
        #scenario_form = dat['scenario_form']
        landuse_formset = dat['landuse_formset']
        if landuse_formset.is_valid():
            form.save()
            landuse_formset.save()
            #UpdatePools(dat['scenario'])
            try:
                UpdatePools(dat['scenario'])
            except AssertionError: #there are no landcovers associated with this ref scenario
                dat['scenario'].delete()
                return HttpResponseRedirect('/ecalc/project/%s' % self.request.session['project_id'])    
            return HttpResponseRedirect('/ecalc/project/%s' % self.request.session['project_id'])
        else:
            return self.render_to_response(self.get_context_data(form=form))  
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    def get_context_data(self,**kwargs):
        context = super(UpdateScenarioView, self).get_context_data(**kwargs)
        scenario = context['scenario']
        context['listurl'] = context['project'].geturl('ecalc-referencescenarios')  
        if self.request.POST:
            #context['scenario_form'] = Scenario_Form(self.request.POST, instance=scenario)
            context['landuse_formset'] = LandUse_FormSet(self.request.POST, instance=scenario, prefix=scenario.project.id)
            context['landuse_formset'].full_clean()
        else:
            #context['scenario_form'] = Scenario_Form(instance=scenario)
            context['landuse_formset'] = LandUse_FormSet(instance=scenario, prefix=scenario.project.id)
        return context    

class UpdateProjScenarioView(UpdateScenarioView):
    def get_context_data(self,**kwargs):
         context = super(UpdateProjScenarioView, self).get_context_data(**kwargs)
         context['listurl'] = context['project'].geturl('ecalc-projectscenarios')
         return context  
 
class RefScenarioListView(ListView_):
    model = Scenario
    template_name = 'ecalc/referencescenario_list.html'
    def get_context_data(self, **kwargs):
        context = super(RefScenarioListView, self).get_context_data(**kwargs)
        context['refscenario_list'] = context['project'].scenario_set.filter(reference_scenario__isnull=True)
        return context
    
class ProjScenarioListView(ListView_):
    model = Scenario
    template_name = 'ecalc/projectscenario_list.html'
    def get_context_data(self, **kwargs):
        context = super(ProjScenarioListView, self).get_context_data(**kwargs)
        context['projscenario_list'] = context['project'].scenario_set.exclude(reference_scenario__isnull=True)
        return context    
 

class CarbonPoolsView(ListView_):
    model = Scenario
    template_name = 'ecalc/carbonpools_list.html'
    def get_queryset(self):
        self.project = None
        #get_queryset = super(CarbonPoolsView, self).get_queryset()
        scenario = get_object_or_404(Scenario,id=self.kwargs['spk'])
        return CarbonPools.objects.filter(scenario=scenario)


def createtest(request, name):
    """ so you don't have to fill out the form for testing """
    try:
        Project.objects.get(owner=request.user, name=name)
        # If get project, then re-create ?
    except Project.DoesNotExist:
        # Create new project
        proj = Project(name=name, owner=request.user, duration=30,
            continent=Continent.objects.get(name='Africa'),
            climate_zone=Climate_Zone.objects.get(name='Tropical'),
            moisture_zone=Moisture_Zone.objects.get(name='Dry'),
            soil_type=Soil_Type.objects.get(name='Sandy'))
        proj.save()
        # Land Covers
        lc1 = (LandCover.objects.filter(project=proj))[0]
        lc2 = LandCover.objects.get(project=proj,name='Annual Crop')
        #lc2 = LandCover(project=proj,name='crop',category='A',biomassa=40.0,soil=40.0)
        #lc2.save()
        # Practice
        pr1 = Practice(project=proj,name="Practices1")
        pr2 = Practice(project=proj,name="Practices2")
        pr1.save()
        pr2.save()   
        # Parcels
        parcel1 = Parcel(project=proj,name='Parcel 1',area=10.0,initial_lc=lc1)
        parcel1.save()
        #parcel2 = Parcel(project=proj,name='Parcel 2',area=15.0,initial_lc=crop)
        #parcel2.save()
        # Scenarios
        sc1 = Scenario(project=proj,name='Baseline',parcel=parcel1)
        sc1.save()
        sc2 = Scenario(project=proj,name='Test Scenario',parcel=parcel1)
        sc2.save()
        # LandUse added to scenario
        LandUse(scenario=sc1,landcover=lc1,start_year=0,practice=pr1).save()
        LandUse(scenario=sc2,landcover=lc2,start_year=0,practice=pr2).save()
        sc1.save()
        sc2.save()
        UpdatePools(sc1)
        UpdatePools(sc2)
        # Redirect to somewhere useful
    #p = get_object_or_404(Project,name=name)
    #return render_to_response('ecalc/detail.html', {'project': p})
    return HttpResponseRedirect(reverse('ecalc-projects'))

from utils import load_ipcc

@login_required
def setup(request):
    """ load database input tables from spreadsheet """
    try:
        if request.user.is_staff:
            result = load_ipcc()
        #response += str(result)
        #response += "<p>tables have been loaded"
        return HttpResponseRedirect('/ecalc/')
    except Exception, e:
        response = "there was an error setting up the IPCC tables: %s<p>" % e
        return HttpResponse(response)


#class PrepopulateProjectView(UpdateView)
#    form = PrepopulateProjectForm

