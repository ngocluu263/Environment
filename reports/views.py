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


import ho.pisa
import StringIO
import os, tempfile
from mrv_toolbox import settings

from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect 
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.views.generic import View, CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context
from mrvapi.models import Project, Region, Country, Parcel, ProjectPermissions, Documents, Plot
from ecalc.ipcc import *
from core.forms import AddUserForm, AEQForm, CopyProjectForm, CreateProjectForm, EditProjectForm, CreateParcelForm, AddUserProjectForm, CreateFolderForm, DocumentUploadForm
from mrvapi.v1 import CountryResource, RegionResource
from django.contrib import messages
from allometric.models import Equation



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

def fetch_resources(uri, rel):
    path = os.path.join(settings.PROJECT_HOME, 'static/')
    path = os.path.join(path, uri.replace('static/', ''))

    return path


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = ho.pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result, link_callback=fetch_resources)    
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype="application/pdf", status=200)
    return HttpResponse('We had some errors', status=400)


class ReportingView(MixinView, TemplateView):
    template_name = 'reports/reporting.html'

def projectInfoReportView(request, pk):
    pk = int(pk)
    report_type = request.GET.get('type', '1')
    project = Project.objects.get(id=pk)    
    response = None
    if report_type == '1':
        return render_to_pdf('reports/project_info_report.html', {'project':project})

    if report_type == '2':	
        parcels = Parcel.objects.filter(project = project)            
        plots = Plot.objects.filter(parcel__in=parcels) 
        template = 'reports/report_carbon.html' 
        context = {'project':project,'parcels':parcels,'plots':plots}           
        return render_to_pdf('reports/report_carbon.html', {'project':project,'parcels':parcels,'plots':plots})             
    return response




class ProjectInfoReportView(MixinView, TemplateView):
    template_name = 'reports/project_info_report.html'
    
    def get_context_data(self, **kwargs):
        context = super(ProjectInfoReportView, self).get_context_data(**kwargs)
        project = Project.objects.get(id=kwargs['pk'])
        context['project'] = project
        return context

class CarbonStocksReportView(MixinView, TemplateView):
    template_name = ''
