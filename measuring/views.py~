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
# Create your views here.
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.views.generic import View, CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mrvapi.models import Project, Region, Country, Parcel, ProjectPermissions, ProjectBoundary
from measuring.models import ImageModel
from allometric.models import EquationRegion, Equation, EquationCountry
from ecalc.ipcc import *
from mrvapi.v1 import CountryResource, RegionResource
from django.contrib import messages
from measuring.forms import *
from django.views.decorators.csrf import csrf_exempt
import os, tempfile
from django.core.servers.basehttp import FileWrapper
import math
from tasks import *
from celery.result import AsyncResult
import ingest

class MixinView(View):
    """ The purpose of this MixIn View is to disallow all
    unauthorized users access to a specific view.

    Extends:
    View
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """ The purpose of this method is to return a response for this
        view.
        Args:
        args -- Contains the request, as well as some other arguments
        kwargs -- keyword arguments
        Returns:
        Default view response for valid/invalid login attempt
        """
        return super(MixinView, self).dispatch(*args, **kwargs)

class InventoryPlanningView(MixinView, TemplateView):
    template_name = 'measuring/inventory_planning.html'

class DataManagementView(MixinView, TemplateView):
    template_name = 'measuring/data_manage.html'
    def get_context_data(self, **kwargs):
        project = None
        country = None
        regions = None
        context = super(DataManagementView, self).get_context_data(**kwargs)
        project = Project.objects.get(id=kwargs['pk'])
        try:
            country = EquationCountry.objects.get(name__icontains=project.country)
        except:
            country = None
        if country:
            regions = EquationRegion.objects.filter(country = country)
        equations = Equation.objects.filter(region=None, species=None)
        context['equations'] = equations
        context['regions'] = regions

        return context

class CarbonCalculationsView(MixinView, TemplateView):
    template_name = 'measuring/carbon_calculations.html'

    def get_context_data(self, **kwargs):
        #calculateTotalCarbonStocks.delay(Project.objects.get(id=kwargs['pk']))
        context = super(CarbonCalculationsView, self).get_context_data(**kwargs)
        context['parcels'] = Parcel.objects.filter(project = kwargs['pk']).order_by('name')
        context['project'] = Project.objects.get(id=kwargs['pk'])
        return context

class ParcelManageBBProof(MixinView, TemplateView):
    template_name = 'measuring/parcel_manage_backbone.html'


def MassDataUpload(request, project_id):
    project = Project.objects.get(id=project_id)

    f = request.FILES["parcelData"]

    ingestTool = ingest.IndonesianPlotIngest(f, project)
    try:
        ingestTool()
    except Exception as e:
        messages.add_message(request, messages.ERROR, e.args)
        return HttpResponseRedirect(reverse('data-management', kwargs={'pk':project_id}))

    calculateTotalCarbonStocks.delay(project_id)
    messages.add_message(request, messages.SUCCESS, "Upload Successful")
    return HttpResponseRedirect(reverse('data-management', kwargs={'pk':project_id}))


# def send_file(request):
#     '''
#     Send a file through Django without loading the whole file
#     into memory at once. The FileWrapper will return the file object into
#     an iterator for chucks of 8 KB
#     '''
#     filename =


class ParcelManagementView(MixinView, TemplateView):
    template_name = 'measuring/parcel_manage.html'
    def get_context_data(self, **kwargs):
        context = super(ParcelManagementView, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(id = self.request.session['project_id'])
        mapped_area = 0.0
        boundaries = ProjectBoundary.objects.filter(project = self.request.session['project_id'])
        for boundary in boundaries:
            mapped_area += boundary.area_mapped

        context['areaMapped'] = round(mapped_area, 2)
        context['parcels'] = Parcel.objects.filter(project = self.request.session['project_id']).order_by('name')

        #calculateTotalCarbonStocks.delay(project.id)
        #calculateTotalCarbonStocks.delay(Project.objects.get(id=kwargs['pk']))
        return context

class PlotInventoryReview(MixinView, UpdateView):
    template_name = 'measuring/data_manage_biomass_review.html'
    model = Plot

    def get_context_data(self, **kwargs):
        context = super(PlotInventoryReview, self).get_context_data(**kwargs)
        plot = context['plot']
        trees = Tree.objects.filter(plot=context['plot'].id).order_by('excel_row')
        context['trees'] = trees

        return context

class PlotDetailsView(MixinView, UpdateView):
    template_name = 'measuring/plotDetails.html'
    model = Plot
    def get_context_data(self, **kwargs):
        context = super(PlotDetailsView, self).get_context_data(**kwargs)
        return context

class AddPlotView(MixinView, UpdateView):
    template_name = 'measuring/create_plot.html'
    model = Plot
    def get_context_data(self, **kwards):
        context = super(AddPlotView, self).get_context_data(**kwargs)
        return context

@login_required
def SubmitReportedArea(request, pk):
    project = Project.objects.get(id = pk)    
    if request.method == 'POST':
	form = ModifyReportedAreaForm(request.POST)
	if form.is_valid():
	    project.reported_area = form.cleaned_data['reported_area_project']
	    project.save()
	    return HttpResponse('OK', status=200)
	else:
	    return HttpResponse('Invalid', status=400)    
    return HttpResponse('OK', status=200)
##########################################################################################################################################################################
@login_required
def SubmitParcelReportedArea(request, pk):
    parcel = Parcel.objects.get(id = pk)   
    if request.method == 'POST':
	form = ModifyParcelReportedAreaForm(request.POST)
	if form.is_valid():
	    parcel.area_reported = form.cleaned_data['parcelreportedarea']
	    parcel.save()
	    calculateTotalCarbonStocks(parcel.project_id)           
	    return HttpResponse('OK', status=200)
	else:
	    return HttpResponse('', status=400)   
    return HttpResponse('OK', status=200)
    

#############################################################################################################################################################################
@login_required
def SubmitPlotInformation(request, pk):
    plot = Plot.objects.get(id = pk)
    if request.method == 'POST':
        form = ModifyPlotInformationForm(request.POST)
        if form.is_valid():
            plot.shape_reported = form.cleaned_data['shapeEdit']
            if plot.shape_reported == 'circle':
                plot.dimensions_reported = form.cleaned_data['radiusEdit']
                plot.reported_area = plot.dimensions_reported * plot.dimensions_reported * math.pi
            else:
                plot.dimensions_reported = "{0}x{1}".format(form.cleaned_data['xDimEdit'], form.cleaned_data['yDimEdit'])
                plot.reported_area = form.cleaned_data['xDimEdit'] * form.cleaned_data['yDimEdit']

            plot.root_shoot_ratio = form.cleaned_data['root_shoot_ratio']
            plot.save()

            calculateTotalCarbonStocks.delay(plot.project.id)
            return HttpResponse('OK', status=200)
        else:
            response = HttpResponse('', status=400)
            return response
    #calculateTotalCarbonStocks.delay(Project.objects.get(id=kwargs['pk']))
    return HttpResponse('OK', status=200)

@csrf_exempt
def AddParcel(request, pk):
    project = Project.objects.get(id = pk)
    if request.method == 'POST':
        form = AddParcelForm(request.POST)
        if form.is_valid():
            parcel = Parcel()
            parcel.project = project
            parcel.name = form.cleaned_data['parcel_name']
            parcel.area_reported = form.cleaned_data['parcel_area']
            parcel.save()
            return HttpResponse('%s,%d' % (parcel.name, parcel.id),status=200 )
        else:
            return HttpResponse('Invalid', status=400)
    #calculateTotalCarbonStocks.delay(project.id)
    return HttpResponse('OK', status=200)

@csrf_exempt
def deletePlot(request, pk):
    try:
        plot = Plot.objects.get(id=pk)
    except:
        return HttpResponse('Unable to get plot', code=400)

    plot.delete()

    messages.add_message(request, messages.SUCCESS, 'Delete the plot.')

    return HttpResponseRedirect(('/measuring/manage_parcels_plots/save%s/' % request.session['project_id']))

class ManageParcelsPlotsView(MixinView, TemplateView):
    template_name = 'measuring/plot_parcel_manage.html'

    def get_context_data(self, **kwargs):
        context = super(ManageParcelsPlotsView, self).get_context_data(**kwargs)

        project = Project.objects.get(id = self.request.session['project_id'])

        context['project'] = project

        parcels = Parcel.objects.filter(project = project.id).order_by('name')
        hidden_parcel = Parcel.objects.hidden_set().get(project = project.id)
        context['hiddenparcel'] = hidden_parcel
        allometricequations = Equation.objects.filter(region=None, species=None)
        context['equations'] = allometricequations
        context['parcels'] = parcels
        #calculateTotalCarbonStocks.delay(project.id)
        return context

class ImageUploadTest(MixinView, TemplateView):
    template_name = 'measuring/image_upload.html'

    def get_context_data(self, **kwargs):
        context = super(ImageUploadTest, self).get_context_data(**kwargs)
        project = Project.objects.get(id = self.request.session['project_id'])

        context['project'] = project

        plot = Plot.objects.get(id = kwargs['ppk'])

        context['plot'] = plot

        return context

class ImagesView(MixinView, TemplateView):
    template_name = 'measuring/images_view.html'

    def get_context_data(self, **kwargs):
        context = super(ImagesView, self).get_context_data(**kwargs)
        project = Project.objects.get(id = kwargs['pk'])

        context['project'] = project

        plot = Plot.objects.get(id = kwargs['ppk'])

        context['plot'] = plot

        Images = ImageModel.objects.filter(plot = plot)

        context['images'] = Images

        return context

class ImageView(MixinView, TemplateView):
    template_name = 'measuring/image_view.html'

    def get_context_data(self, **kwargs):
        context = super(ImageView, self).get_context_data(**kwargs)
        context['image'] = ImageModel.objects.get(id = kwargs['pk'])
        return context

@login_required
def SaveParcelsPlots(request, pk):
    project = Project.objects.get(id = pk)
    if request.method == 'POST':
        form = SaveParcelsPlotsForm(request.POST)
        if form.is_valid():
            #calculateTotalCarbonStocks.delay(project.id)
            return HttpResponse('OK', status=200)
        else:
            return HttpsResponse('', status=400)
    calculateTotalCarbonStocks.delay(project.id)
    return HttpResponseRedirect('/measuring/manage_parcels_plots/%s/' % (request.session['project_id'], ))


def WebImageUpload(request, pk, ppk):
    plot = Plot.objects.get(id = ppk)
    if request.method == 'POST':
        form = AddImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = ImageModel(image = request.FILES['image'])
            img.name = form.cleaned_data['name']
            img.plot = plot
            img.save()
            messages.add_message(request, messages.SUCCESS, 'Successfuly added image.')
            return HttpResponseRedirect('/measuring/image_management/%s/%s/' % (request.session['project_id'], plot.id))
        else:
            messages.add_message(request, messages.ERROR, 'Something went wrong.')
            return HttpResponseRedirect('/measuring/image_management/%s/%s/add/' % (request.session['project_id'], plot.id))
    #calculateTotalCarbonStocks.delay(Project.objects.get(id=kwargs['pk']))
    messages.add_message(request, request.WARNING, 'Wrong request type.')
    return HttpResponseRedirect('/measuring/image_management/%s/%s/' % (request.session['project_id'], plot.id))

@csrf_exempt
def ImageUpload(request, pk, ppk):
    plot = Plot.objects.get(id = ppk)
    if request.method == 'POST':
        form = AddImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = ImageModel(image = request.FILES['image'])
            img.name = form.cleaned_data['name']
            img.plot = plot
            img.save()
            #calculateTotalCarbonStocks.delay(Project.objects.get(id=kwargs['pk']))
            return HttpResponse('Success', status=200)

        else:
            return HttpResponse('Invalid', status=400)
    return HttpResponse('OK', status=200)

def ImageDelete(request, pk, ppk, pppk):
    plot = Plot.objects.get(id=ppk)
    img = ImageModel.objects.get(id = pppk)
    img.delete()
    return HttpResponseRedirect('/measuring/image_management/%s/%s/' % (pk, ppk))

def recalculate(request, pk):
    calculateTotalCarbonStocks.delay(pk)
    return HttpResponse(status=200)
