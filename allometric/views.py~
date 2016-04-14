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
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.views.generic import View, CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from allometric.models import *
from allometric.forms import *
from mrvapi.models import Plot, Parcel,Project,Tree
import allometric.aeq
from measuring.tasks import *

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

class GroupSpecies(MixinView, ListView):
    template_name = 'allometric/species_groups.html'
    model = EquationSpecies

    def get_context_data(self, **kwargs):
        context = super(GroupSpecies, self).get_context_data(**kwargs)
        #genus_species = self.request.GET.get('species')
        #genus = self.request.GET.get('genus')
        eqtnspecies = EquationSpecies.objects.all()
        object_list = None

        """if genus:
            object_list = (Equation.objects.filter(owner=request.user, species__genus=genus) | Equation.objects.filter(public=True, species__genus = genus).order_by('public', 'name'))
            title = "Available Allometric Equations for Genus: %s" % (genus)

        #Display Species List
        elif genus_species and genus is None:
            #split genus_species
            genus_species = genus_species.split("-")
            genus = genus_species[0]
            species = genus_species[1]

            #formatting
            genus = genus.strip()
            genus = genus.capitalize()
            object_list = (Equation.objects.filter(owner=self.request.user, species__name=species, species__genus=genus) | Equation.objects.filter(public=True, species__name = species, species__genus = genus).order_by('public', 'name'))
            title = "Available Allometric Equations for %s %s" % (genus, species)

        context['queryset'] = object_list
        """
        genus_list = []
        for item in eqtnspecies:
            igenus = item.genus.strip()
            igenus = igenus.title()
            genus_list.append(igenus)

        genus_set = set(genus_list) #DELETES DUPLICATES
        genus_list = list(genus_set)
        genus_list.sort()

        context['genus'] = genus_list

        species_list = []
        species_names = set()
        for item in eqtnspecies:
            igenus = item.genus.strip()
            igenus = igenus.title()
            ispecies = item.name.strip()
            ispecies = ispecies.lower()
            full_name = "%s %s" % (igenus, ispecies)
            if full_name not in species_names:
        		species_names.add(full_name)
        		species_list.append(item)
        species_set = set(species_list) #DELETES DUPLICATES
        species_list = list(species_set)
        species_list.sort()

        context['species'] = species_list

        return context


    class Meta:
        ordering = ['genus']

class CreateSpecies(MixinView, CreateView):
    template_name = 'allometric/species_form.html'
    model = EquationSpecies
    form_class = SpeciesForm

    def get_success_url(self):
        return reverse("species_list")


class GroupAEQ(MixinView, ListView):
    template_name = 'allometric/aeq_groups.html'
    model = Equation
    queryset = EquationRegion.objects.all()
    def get_context_data(self, **kwargs):
        context = super(GroupAEQ, self).get_context_data(**kwargs)
        context['countries'] = EquationCountry.objects.all()
        context['categories'] = EquationCategory.objects.all()
        eqtnspecies = EquationSpecies.objects.all()

        genus = []
        for item in eqtnspecies:
            igenus = item.genus.strip()
            if igenus not in genus:
                genus.append(igenus)
        genus.sort()
        genus = set(genus)
        context['genus'] = genus

        specienames = []
        species = set()
        for item in eqtnspecies:
            if item.name not in specienames:
                specienames.append(item.name)
                species.add(item)
        context['species'] = species
        return context
    class Meta:
        ordering = ['name']

class UploadAEQ(MixinView, TemplateView):
    template_name = 'allometric/upload_aeq.html'

class CreateAEQ(MixinView, CreateView):
    template_name = 'allometric/aeq_form.html'
    model = Equation
    form_class = AEQForm

    def get_success_url(self):
        return reverse(aeq_list)

    def form_valid(self, form):
        # Override #1 - force the owner field to be request.user
        form.instance.owner = self.request.user

        if form.cleaned_data['genus']:
            try:
                if not form.cleaned_data['species_text_field']:
                    equationspecies = EquationSpecies.objects.get(genus__iexact=form.cleaned_data['genus'])
                else:
                    equationspecies = EquationSpecies.objects.get(genus__iexact=form.cleaned_data['genus'], species__iexact=form.cleaned_data['species_text_field'])
            except:
                equationspecies = EquationSpecies()
                equationspecies.genus = form.cleaned_data['genus']
                equationspecies.name = form.cleaned_data['species_text_field']
                equationspecies.save()

            form.instance.species = equationspecies

        return super(CreateAEQ, self).form_valid(form)

class UpdateAEQ(MixinView, UpdateView):
    template_name = 'allometric/aeq_form.html'
    model = Equation
    form_class = AEQForm

    def get_success_url(self):
        return reverse("aeq_list")

    def get_queryset(self):
        # limit query to only user-owned AEQs or else other users can see
        return super(UpdateAEQ, self).get_queryset().filter(owner=self.request.user)

    def dispatch(self, *args, **kwargs):
        # Confirm object is not in use
        #if get_object_or_404(Equation, pk=kwargs['pk']).is_in_public_use:
            #raise Http404
        return super(UpdateAEQ, self).dispatch(*args, **kwargs)


class DeleteAEQ(MixinView, DeleteView):
    template_name = 'allometric/aeq_delete.html'
    model = Equation

    def get_success_url(self):
        return reverse("aeq_list")

    def get_queryset(self):
        # limit query to only user-owned AEQs or else other users can see
        return super(DeleteAEQ, self).get_queryset().filter(owner=self.request.user)

    def dispatch(self, *args, **kwargs):
        # Confirm object is not in use
        #if get_object_or_404(Equation, pk=kwargs['pk']).is_in_use:
            #raise Http404
        return super(DeleteAEQ, self).dispatch(*args, **kwargs)

def aeq_list(request):
    # Get params from URL
    category = request.GET.get('category')
    country = request.GET.get('country')
    region = request.GET.get('region')
    genus_species = request.GET.get('species')
    genus = request.GET.get('genus')

    object_list = None
    species = None
    equationspecies = None
    regions = None
    template = 'allometric/aeq_list.html'

    #Display by category
    if category:
        first = category[0].upper()
        #category = str(category)
        object_list = (Equation.objects.filter(owner=request.user, category__name=first) | Equation.objects.filter(public=True, category__name=first).order_by('public', 'name'))
        title = "Available %s Allometric Equations" % (category.capitalize())

    elif genus:
        object_list = (Equation.objects.filter(owner=request.user, species__genus=genus) | Equation.objects.filter(public=True, species__genus = genus).order_by('public', 'name'))
        title = "Available Allometric Equations for Genus: %s" % (genus)

    #Display Species List
    elif genus_species and genus is None:
        #split genus_species
        genus_species = genus_species.split("-")
        genus = genus_species[0]
        species = genus_species[1]

        #formatting
        genus = genus.strip()
        genus = genus.capitalize()
        object_list = (Equation.objects.filter(owner=request.user, species__name=species, species__genus=genus) | Equation.objects.filter(public=True, species__name = species, species__genus = genus).order_by('public', 'name'))
        title = "%s %s" % (genus, species)
        equationspecies = (EquationSpecies.objects.filter(name=species, genus=genus))
        regions = (EquationRegion.objects.all())
        template = 'allometric/species_list.html'

    #Display by country
    elif country and region is None:
        object_list = (Equation.objects.filter(owner=request.user, region__country__name=country) | Equation.objects.filter(public=True, region__country__name=country).order_by('public', 'name'))
        title = "Available Allometric Equations in %s" % (country)

    #Display by region
    elif country and region:
        region = region.replace("-", " ")
        region = region.title() #capitalize every first letter
        object_list = (Equation.objects.filter(owner=request.user, region__name=region) | Equation.objects.filter(public=True, region__name=region).order_by('public', 'name', 'anatomy', '-less_than_ten'))
        title = "Available Allometric Equations in %s, %s" % (region, country)

    #Display all
    else:
        object_list = (Equation.objects.filter(owner=request.user) | Equation.objects.filter(public=True).order_by('public', 'name', 'anatomy', '-less_than_ten'))
        title = "All Allometric Equations"

    paginator = Paginator(object_list, 25)
    page = request.GET.get('page')

    try:
        equations = paginator.page(page)

    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        equations = paginator.page(1)

    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        equations = paginator.page(paginator.num_pages)

    context = {
            'equations': equations,
            'object_list': object_list,
            'country': country,
            'region': region,
            'regions': regions,
            'category': category,
            'title': title,
            'genus': genus,
            'species': species,
            'equationspecies': equationspecies,
            'mathjax': settings.MATHJAX_CDN_URL
    }

    return render(request, template, context)



@login_required(redirect_field_name='/core/splash/')
def deleteAEQ(request, pk):
    s = ""
    j =0 
    try:
        plotList=Plot.objects.all()        
	for p in plotList:
	    if p.aeq_id == int(pk):
	       p.aeq_id = 1
               p.save() 
               rePlotCalculate(p.id,1)
       
        parcelList=Parcel.objects.all()
	for p in parcelList:
	    if p.aeq_id == int(pk):
	       p.aeq_id = 1
               p.save()
               reParcelCalculate(p.id,1)

        projectList=Project.objects.all()
	for p in projectList:
	    if p.aeq_id == int(pk):
	       p.aeq_id = 1       
               p.save()
               reCalculateTotalCarbonStocks(p.id,1)            
	            
        aeq = Equation.objects.get(id=pk)
    except Equation.DoesNotExist:
        messages.add_message(request, messages.WARNING, 'The requested allometric equation does not exist')
        return HttpResponseRedirect('/allometric/')
    
    if aeq.is_in_use or aeq.id == 1:
        messages.add_message(request, messages.ERROR, 'You cannot delete an allometric equation that is in use or system default equation.')               
        return HttpResponseRedirect('/allometric/')

    try:
        aeq.delete()
    except Exception as e:
        messages.add_message(request, messages.ERROR, 'Unable to delete this allow metric equation %s' % e)
    else:
        messages.add_message(request, messages.SUCCESS, 'Deleted the allometric equation successfully')

    return HttpResponseRedirect('/allometric/')

def uploadAEQ(request):
    if request.method == 'POST':
        try:
            form = AEQUploadForm(request.POST, request.FILES)

            if not form.is_valid():
                raise Exception('Upload is not valid')


            f = request.FILES['aeqsheet']
            equations = f.read()
            equations = equations.splitlines()

            AllometricEquationObjects = []

            for line in equations:
                equation = line.split(',')
                #check if first line
                if 'name' in equation or 'equation string' in equation:
                	continue

                 # We want values to be optional and user errors to be dealt with in the
                # system instead of on the client side.
                #if len(equation) != 8:
                #    raise Exception('The file isn\'t properly formatted. Too few values')

                if equation[0] == '' or not equation[0]:
                    raise Exception('All equations must have a name')

                if not equation[1]:
                    break

                if '=' in equation[1]:
                    raise Exception('Your equation string isn\'t properly formatted')

                aeq_valid = allometric.aeq.is_aeq_invalid(equation[1])
                if aeq_valid:
                    raise Exception(aeq_valid)

                if equation[5].strip().lower() != 'true' and equation[5].strip().lower() != 'false':
                    raise Exception('The file isnt\' properly formatted. Incorrect value for volume.')

                if equation[6].strip().lower() != 'true' and equation[6].strip().lower() != 'false':
                    raise Exception('The file isn\'t properly formatted. Incorrect value for dbh')

                if equation[7].strip().lower() != 'true' and equation[7].strip().lower() != 'false':
                    raise Exception('The file isn\'t properly formatted. Incorrect value for share')

                if equation[3] and equation[4]:
                    try:
                        species = EquationSpecies.objects.get(genus__iexact = equation[3], name__iexact = equation[4])
                    except:
                        messages.add_message(request, messages.WARNING, 'Could not find species specified. Created new species for equation: %s' % equation[0])
                        species = EquationSpecies()
                        species.genus = equation[3]
                        species.name = equation[4]
                        species.save()
                else:
                    messages.add_message(request, message.WARNING, 'No species specified. Will not associate a species with equation: %s' % equation[0])
                    species = None

                try:
                    region = EquationRegion.objects.get(name__iexact = equation[2])
                except:
                    messages.add_message(request, messages.WARNING, 'Could not find the region specified. Will not associate a region with equation: %s' % equation[0])
                    region = None

                eq = Equation()
                eq.name = equation[0].strip()
                eq.string = equation[1].strip()
                eq.owner = request.user
                eq.species = species
                eq.region = region

                if equation[5].strip().lower() == 'true':
                    eq.volumetric = True
                else:
                    eq.volumetric = False

                if equation[6].strip().lower() == 'true':
                    eq.less_than_ten = True
                else:
                    eq.less_than_ten = False

                if equation[7].strip().lower() == 'true':
                    eq.public = True
                else:
                    eq.public = False

                if equation[8]: #category
                	if equation[8].strip().upper() == 'C':
                		eq.category = EquationCategory.CARBON_BENEFITS
                	elif equation[8].strip().upper() == "G":
                		eq.category = EquationCategory.GENERAL
                	else:
                		messages.add_message(request, messages.WARNING, 'Incorrect category. Choices are C or G  Will not associate a category with equation: %s' % equation[0])
               			eq.category = None
               	if equation[9]: #anatomy
               		if equation[9].strip() == "small wood":
               			eq.anatomy = Equation.SMALLWOOD
               		elif equation[9].strip() == "foliage":
               			eq.anatomy = Equation.ANATOMY
               		else:
               			messages.add_message(request, messages.WARNING, 'Could not find anatomy specified.  Will not associate a category with equation: %s' % equation[0])
               			eq.anatomy = None

                AllometricEquationObjects.append(eq)

            Equation.objects.bulk_create(AllometricEquationObjects)
            messages.add_message(request, messages.SUCCESS, 'Successfully uploaded all the equations')
            return HttpResponseRedirect('/allometric/')
        except Exception as e:
            messages.add_message(request, messages.ERROR, '%s' % e)
            return HttpResponseRedirect('/allometric/upload/')

    return HttpResponseRedirect('/allometric/')

