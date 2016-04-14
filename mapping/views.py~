
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
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import os, tempfile
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.views.generic import View, TemplateView
from mrvapi.models import Project, Parcel, Plot, ProjectBoundary
from models import *

# def index(request, pk):
# 	return render_to_response('mapping/mapping_index.html', context_instance=RequestContext(request))

class MixinView(View):
    """ 1) disallows un-auth'd users ... """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MixinView, self).dispatch(*args, **kwargs)

class MappingView(MixinView, TemplateView):
    template_name = 'mapping/mapping_index.html'

@login_required
def SaveMap(request, pk):
    project = Project.objects.get(id = pk)
    if request.method == 'POST':
        return HttpResponse('OK', status=200)
        # else:
        #     return HttpsResponse('', status=400)
    return HttpResponseRedirect('/mapping/%s/' % (request.session['project_id']))

@login_required
def PrintMap(request, pk):
    project = Project.objects.get(id = pk)
    boundaries = ProjectBoundary.objects.filter(project=project)
    parcels = Parcel.objects.filter(project=project)
    plots = Plot.objects.filter(project=project)

    return render_to_response("mapping/mapping_print_page.html",
                            {"project": project,
                             "parcels": parcels,
                             "plots": plots,
                             "boundaries": boundaries},
                             context_instance=RequestContext(request))
