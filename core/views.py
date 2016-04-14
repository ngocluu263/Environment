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





from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect 
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.views.generic import View, CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mrvapi.models import Project, Region, Country, Parcel, ProjectPermissions, Documents
from ecalc.ipcc import *
from core.forms import AddUserForm, AEQForm, CopyProjectForm, CreateProjectForm, EditProjectForm, CreateParcelForm, AddUserProjectForm, CreateFolderForm, DocumentUploadForm
from mrvapi.v1 import CountryResource, RegionResource
from django.contrib import messages
from allometric.models import Equation
import os, tempfile, zipfile
from mrv_toolbox.settings import MEDIA_ROOT

try:
    from functools import wraps
except:
    from django.utils.functional import wraps
#from core.models import cloneproject

##############################################################################
##                                                                          ##
##          README BEFORE CREATING VIEWS                                    ##
##          ----------------------------                                    ##
##  -- When you are creating views, make sure you determine if login        ##
##     should be required for access to the view. If so, make sure you      ##
##     inherit from MixinView (see below).                                  ##
##  -- Don't forget to inherit from the appropriate Generic view (see       ##
##     documentation). A view that is just displaying data, but no form     ##
##     SHOULD NOT be inheriting from UpdateView or FormView.                ##
##  -- When in doubt, refer to the Django Documentation as to what Generic  ##
##     View you should use.                                                 ##
##                                                                          ##
##############################################################################

def require_owner(func):
    def wrap(request, *args, **kwargs):
        perm = ProjectPermissions.objects.get(user=request.user, project=request.session['project_id'])
        if perm.permission != 0:
            raise Exception()
        return func(request, *args, **kwargs)
    return wrap

def require_administrator(func):
    def wrap(request, *args, **kwargs):
        perm = ProjectPermissions.objects.get(user=request.user, project=request.session['project_id'])
        if perm.permission != 0 and perm.permission != 1:
            raise Exception()
        return func(request, *args, **kwargs)
    return wrap

def project_permission_required(func):
    def wrap(request, *args, **kwargs):
        try:
            perm = ProjectPermissions.objects.get(user=request.user, project=request.session['project_id'])
        except Exception as e:
            raise Exception()

        return func(request, *args, **kwargs)
    return wrap



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

class MixinAdmin(View):

    @method_decorator(login_required)
    @method_decorator(require_administrator)
    def dispatch(self, *args, **kwargs):
        return super(MixinAdmin, self).dispatch(*args, **kwargs)

class AccountView(MixinView, TemplateView):
    template_name = 'core/account.html'

class SettingsView(MixinView, TemplateView):
    template_name = 'core/settings.html'


class BulletinContextView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(BulletinContextView, self).get_context_data(**kwargs)

        context['bulletin_true'] = settings.BULLETIN_TRUE
        context['bulletin_heading'] = settings.BULLETIN_HEADING
        context['bulletin_message'] = settings.BULLETIN_MESSAGE
        context['bulletin_color'] = settings.BULLETIN_COLOR
        context['bulletin_date'] = settings.BULLETIN_DATE

        # TODO: Recent projects
        context['recent_projects'] = [{'name': 'Demo Project 1', 'updated': 'Yesterday'},
                                      {'name': 'Demo Project 2', 'updated': '2 days ago'}]

        # TODO: Recent changes
        context['recent_changes'] = [{'name': 'Change 1', 'updated': '2 days ago'},
                                     {'name': 'Change 2', 'updated': '2 days ago'}]

        # TODO: Support tickets
        context['support_tickets'] = []

        # TODO: Messages
        context['messages_inbox'] = []

        return context


class ProjectDashboardView(MixinView, TemplateView):
    template_name = 'core/project_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDashboardView, self).get_context_data(**kwargs)

        context['project'] = self.request.session['project']

        return context


class SplashView(MixinView, BulletinContextView):
    template_name = 'core/splash.html'


class UtilitiesView(MixinView, TemplateView):
    template_name = 'core/utilities.html'

@login_required(redirect_field_name='/core/splash/')
def switchproject(request, project_id):
    """ The purpose of this function view is to redirect to a project
        after the user selects a new project. 
        This function will update the project in the user session to
        be the new project.
        ARGS:
            request - The request placed by the browser
            project_id - The project id that will be placed in the urlresolvers
        RETURNS:
            HttpReponseRedirect -- Redirects to the review project page, passing
            in the project_id above
    """
    request.session['project_id'] = project_id
    p = ProjectPermissions.objects.get(project=project_id, user=request.user)
    request.session['perm'] = p.permission
    return HttpResponseRedirect("/../core/review_project/%s" % project_id)

@login_required(redirect_field_name='/core/splash/')
def deleteproject(request, pk):
    """ The purpose of this function view is to remove the project from a user's
        session. It will then redirect user to the splash page.
        ARGS:
            request - The request placed by the browser
        RETURNS:
            HttpReponseRedirect -- Redirects user to the splash page.
    """
    try:
        proj = Project.objects.get(id=pk)
    except Project.DoesNotExist:
        messages.add_message(request, messages.ERROR, "That project does not exist")
        return HttpResponseRedirect('/../core/splash/')
    else:
        proj.delete()

    try:
        for folder in Documents.objects.filter(project=request.session['project']):
            folder.delete()
        for permission in ProjectPermissions.objects.filter(project=request.session['project']):
            permission.delete()
        del request.session['project']

    except KeyError:
        pass
    else:
        messages.add_message(request, messages.SUCCESS, "Project has been deleted.")
    return HttpResponseRedirect('/../core/splash/')

@login_required(redirect_field_name='/core/splash/')
def deleteFolder(request, pk, ppk):
    try:
        folder = UploadFolder.objects.get(id=ppk)
        uploads = Upload.objects.filter(folder = folder)
    except folder.DoesNotExist:
        return HttpResponse('', status=404)
    else:
        uploads.delete()
        folder.delete()

    return HttpResponse('Accepted', status=200)

def documentUpload(request, pk, ppk):
    if request.method == 'POST':
        project = None
        parent = None
        try:
            form = DocumentUploadForm(request.POST, request.FILES)
            project = Project.objects.get(id=pk)
            parent = Documents.objects.get(id=ppk)
        except Exception as e:
            return HttpResponse(e, status=400)

        if form.is_valid():
            document = Documents()
            if form.cleaned_data['name']:
                document.text = form.cleaned_data['name']
            else:
                document.text = request.FILES['upload'].name

            document.upload = request.FILES['upload']
            document.project = project
            document.parent = parent

            document.save()
        else:
            return HttpResponse('Invalid Form', status=403)

        return HttpResponse('OK', status=200)

    return HttpResponse('Invalid Request', status=405)

# """                                                                         
# Send a zip through Django without loading the whole file into              
# memory at once. The FileWrapper will turn the file object into an           
# iterator for chunks of 8KB.                                                 
# """
def zipDownload(request, pk):
    selected_file = Documents.objects.get(id=pk)

    archive_name = "%s.zip" % (selected_file.text)

    upload_path = selected_file.upload

    if selected_file.upload:
        temp = tempfile.TemporaryFile()
        
        archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        filename = "%s%s" % (MEDIA_ROOT, selected_file.upload)
        archive.write(selected_file.upload.path, os.path.basename(selected_file.upload.path))
        archive.close()
        wrapper = FileWrapper(temp)
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = "attachment; filename=%s" % archive_name
        response['Content-Length'] = temp.tell()
        temp.seek(0)
        return response
    else:
        temp = tempfile.TemporaryFile()
        archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        builtDirectory = buildDirectory(pk, archive, p=selected_file.text)
        archive.close()
        wrapper = FileWrapper(temp)
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = "attachment; filename=%s" % archive_name
        response['Content-Length'] = temp.tell()
        temp.seek(0)
        return response

def buildDirectory(id, temp_archive, p):
    children = Documents.objects.filter(parent=id)

    for child in children:
        if child.upload:
            temp_archive.write(child.upload.path, "%s/%s" % (p, os.path.basename(child.upload.path)))
        else:
            current_path = "%s/%s" % (p, child.text)
            buildDirectory(child.id, temp_archive, current_path)

class CopyProjectView(MixinView, FormView):
    template_name = 'core/copy_project_form.html'
    form_class = CopyProjectForm

    def get_success_url(self):
        return reverse("copy_project_success")

    def form_valid(self, form):
        # The form should have a form.project member after validation is complete
        form.project.clone(self.request.user)
        return super(CopyProjectView, self).form_valid(form)


class CopyProjectSuccessView(MixinView, TemplateView):
    template_name = 'core/copy_project_success.html'


def CopyProjectResetSecretView(request, pk):
    project = Project.objects.get(id=pk)
    if project.owner == request.user:  # Permission check!
        return HttpResponse(project.reset_secret_code())  # Reset the code and return as HttpResponse
    else:
        return HttpResponse('Unauthorized', status=401)

class EditProjectView(MixinView, UpdateView):
    model = Project
    form_class = EditProjectForm
    template_name = 'core/edit_project_form.html'


    def get_success_url(self):
        self.request.session['project_id'] = self.object.id;
        return reverse('review-project', args=[self.object.id])

    def form_valid(self, form):
        temp_region = form.instance.region
        temp_region = temp_region[0:10].lower()
        form.instance.continent = Continent.objects.get(name__icontains = temp_region)
        return super(EditProjectView, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'You did not correctly fill out the form.')
        return super(EditProjectView, self).form_invalid(form)

class ReviewProjectView(MixinView, DetailView):
    model = Project
    project = Project.objects.all()
    template_name = 'core/review_project_form.html'
    
    def get_object(self):
        object = super(ReviewProjectView, self).get_object()
        return object

class CreateProjectView(MixinView, CreateView):
    model = Project
    form_class = CreateProjectForm
    template_name = 'core/project_form.html'

    def get_success_url(self):
        #return reverse("switch-project", kwargs={'project_id': self.object.id})
        #return switchproject_after_create(request, self.object.id)
        self.request.session['project_id'] = self.object.id

        # Creates initial permissions for project with
        # the owner data
        self.permissions = ProjectPermissions()
        self.permissions.user = self.request.user
        self.permissions.project = self.object
        self.permissions.permission = 0
        self.permissions.save()
        return reverse('edit-project', kwargs={'pk' : self.object.id})

    def form_valid(self, form):
        # Override #1 - force the owner field to be request.user
        form.instance.owner = self.request.user



        return super(CreateProjectView, self).form_valid(form)
    def form_invalid(self, form):
        raise Exception()

class AddUserProject(MixinView, FormView):
    form_class = AddUserProjectForm
    model = ProjectPermissions
    template_name = 'core/add_user_project.html'

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Added user to the project')
        proj = self.request.session['project_id']
        return reverse('add-user-project', kwargs={'pk': proj })

    def form_valid(self, form):
        permissions = ProjectPermissions()
        permissions.user = User.objects.get(username = form.cleaned_data['user_name'])
        permissions.project = Project.objects.get(id = self.request.session['project_id'])
        permissions.permission = form.cleaned_data['permission_level']
        permissions.save()
        # permissions.clone(permissions.project)

        return super(AddUserProject, self).form_valid(form)


class AddUserView(CreateView):
    model = User
    form_class = AddUserForm
    template_name = 'core/add_user_form.html'

    def get_success_url(self):
        return reverse("add_user")

    def form_valid(self, form):
        # This function is called after form has been validated successfully
        return super(AddUserView, self).form_valid(form)

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(AddUserView, self).dispatch(*args, **kwargs)

class ListUsersProject(MixinView, ListView):
    model = ProjectPermissions
    template_name = "core/list_users_project.html"

    def get_queryset(self):
        project = Project.objects.get(id = self.request.session['project_id'])
        return ProjectPermissions.objects.filter(project=project)


class ListAEQ(MixinView, ListView):
    template_name = 'core/aeq_list.html'
    model = Equation

    class Meta:
        ordering = ['-public']

    def get_queryset(self):
        return (Equation.objects.filter(owner=self.request.user) | Equation.objects.filter(public=True)).order_by('public', 'name')


class CreateAEQ(MixinView, CreateView):
    template_name = 'core/aeq_form.html'
    model = Equation
    form_class = AEQForm

    def get_success_url(self):
        return reverse("aeq_list")

    def form_valid(self, form):
        # Override #1 - force the owner field to be request.user
        form.instance.owner = self.request.user

        return super(CreateAEQ, self).form_valid(form)

class ProjectSettingsView(MixinAdmin, DetailView):
    template_name = 'core/project_settings.html'
    model = Project

    def get_context_data(self, **kwargs):
        context = super(ProjectSettingsView, self).get_context_data(**kwargs)
        return context


def CopyProjectSettings(request, pk):
    project = Project.objects.get(id=pk)

    if project.owner == request.user:  # Permission check!
        
        user = User.objects.get(username=request.POST['owner'])

        project.clone(new_owner=user,new_name=request.POST['name']) #Original clone function in models

        # user = User.objects.get(username=request.POST['owner'])
        # #raise Exception("test")
        # new_project = project.cloneProject(new_owner=user, new_name=request.POST['name'])
        #new_project = ProjectClone(project=project,new_owner=user,new_name=request.POST['name'])
        #new_project = cloneproject(pk,new_owner=user,new_name=request.POST['name'])
        

        return HttpResponseRedirect("/core/project-settings/" + pk)
        # return HttpResponse("" + request.POST['name'])
    else:
        return HttpResponse('Unauthorized', status=401)

class UpdateAEQ(MixinView, UpdateView):
    template_name = 'core/aeq_form.html'
    model = Equation
    form_class = AEQForm

    def get_success_url(self):
        return reverse("aeq_list")

    def get_queryset(self):
        # limit query to only user-owned AEQs or else other users can see
        return super(UpdateAEQ, self).get_queryset().filter(owner=self.request.user)

    def dispatch(self, *args, **kwargs):
        # Confirm object is not in use
        if get_object_or_404(Equation, pk=kwargs['pk']).is_in_public_use:
            raise Http404
        return super(UpdateAEQ, self).dispatch(*args, **kwargs)


class DeleteAEQ(MixinView, DeleteView):
    template_name = 'core/aeq_delete.html'
    model = Equation

    def get_success_url(self):
        return reverse("aeq_list")

    def get_queryset(self):
        # limit query to only user-owned AEQs or else other users can see
        return super(DeleteAEQ, self).get_queryset().filter(owner=self.request.user)

    def dispatch(self, *args, **kwargs):
        # Confirm object is not in use
        if get_object_or_404(Equation, pk=kwargs['pk']).is_in_use:
            raise Http404
        return super(DeleteAEQ, self).dispatch(*args, **kwargs)

@login_required(redirect_field_name='/core/splash/')
def deleteAEQ(request, pk):
    try:
        aeq = Equation.objects.get(id=pk)
    except Equation.DoesNotExist:
        messages.add_message(request, messages.WARNING, 'The requested allometric equation does not exist')
        return HttpResponseRedirect('/core/utilities/aeq/')

    if aeq.is_in_use or aeq.id == 1:
        messages.add_message(request, messages.ERROR, 'You cannot delete an allometric equation that is in use.')
        return HttpResponseRedirect('/core/utilities/aeq/')

    try:
        aeq.delete()
    except Exception as e:
        messages.add_message(request, messages.ERROR, 'Unable to delete this allow metric equation %s' % e)
    else:
        messages.add_message(request, messages.SUCCESS, 'Deleted the allometric equation successfully')

    return HttpResponseRedirect('/core/utilities/aeq/')

def debug(request):
    return HttpResponse(str("debug"))

class CreateParcelView(MixinView, FormView):
    model = Parcel
    form = CreateParcelForm

class ProjectDocumentsView(MixinView, FormView):
    form_class = CreateFolderForm
    template_name = 'core/project_documents.html'

    def get_success_url(self):
        return reverse('project-documents', kwargs={'pk' : self.request.session['project_id'] })
    
    def get_context_data(self, **kwargs):
        context = super(ProjectDocumentsView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        Folder = Documents()
        p = Project.objects.get(id=self.request.session['project_id'])
        Folder.project = p
        Folder.text = form.cleaned_data['name']
        Folder.save()
        messages.add_message(self.request, messages.SUCCESS, 'Folder created')
        return super(ProjectDocumentsView, self).form_valid(form)

    def form_invalid(self,form):
        messages.add_message(self.request, messages.ERROR, 'An error occurred. Please try again.')
        return super(ProjectDocumentsView, self).form_invalid(form)
