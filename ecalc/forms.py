from django.forms.models import modelformset_factory, inlineformset_factory, BaseInlineFormSet, BaseModelFormSet
from django import forms
from mrvapi.models import Project
from models import *
from widgets import SelectWithPopUp
from django.core.exceptions import ValidationError
#from django import forms
from django.forms import ModelForm, ModelChoiceField, ModelMultipleChoiceField, ChoiceField
from mrvapi.models import Region, Country

class ReportWizardScenarioForm(forms.ModelForm):
    scenario = forms.ModelChoiceField(queryset=Scenario.objects.none(),
                                      widget=forms.RadioSelect,
                                      empty_label=None,
                                      help_text='Select the project scenarios to report.',
                                      required=False)

    class Meta:
        model = Parcel
        fields = ('scenario', )

    def __init__(self, *args, **kwargs):
        super(ReportWizardScenarioForm, self).__init__(*args, **kwargs)

        # Override 1) Filter the queryset for project scenarios that belong to the parcel
        self.fields['scenario'].queryset = Scenario.objects.filter(parcel=self.instance, reference_scenario__isnull=False)


class ReportWizardScenarioFormsetBase(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        kwargs['queryset'] = Parcel.objects.filter(project=self.project).order_by('name')
        super(ReportWizardScenarioFormsetBase, self).__init__(*args, **kwargs)

ReportWizardScenarioFormset = modelformset_factory(Parcel, formset=ReportWizardScenarioFormsetBase, form=ReportWizardScenarioForm)


class Project_Form(forms.ModelForm):
    region = ChoiceField(choices=tuple(map(lambda x: (x.name, x.name), Region.objects.all())))
    country = ChoiceField(choices=tuple(map(lambda x: (x.name, x.name), Country.objects.all())))
    country_address = ChoiceField(choices=tuple(map(lambda x: (x.name, x.name), Country.objects.all())))

    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        exclude.remove('owner')
        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError, e:
            self._update_errors(e.message_dict)

    class Meta:
        model = Project
        exclude = ('owner', 'reported_area')

Project_FormSet = modelformset_factory(Project)


class BaseForm(forms.ModelForm):
    def __init__(self, project=None, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)


class LandCover_Form(BaseForm):
    class Meta:
        model = LandCover
        exclude = ('project',)

LandCover_FormSet = inlineformset_factory(Project, LandCover, extra=2)


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        include = ('cdm');

class Practice_Form(BaseForm):
    #agricultural_practices = forms.ModelMultipleChoiceField(Agricultural_Practice.objects.all(),
    #    widget=FilteredSelectMultiple("Agricultural Practices",False,attrs={'rows':'5'}))
    class Meta:
        model = Practice
        exclude = ('project',)


class Parcel_Form(BaseForm):
    #initial_lc = forms.ModelChoiceField(LandCover.objects, widget=SelectWithPopUp(model=LandCover))

    def __init__(self, *args, **kwargs):
        super(Parcel_Form, self).__init__(*args, **kwargs)
        try:
            self.fields['initial_lc'].queryset = LandCover.objects.filter(project=self.instance.project)
            self.fields['initial_lc'].widget.url = self.instance.project.geturl(LandCover.get_newpu_urlname())
            self.fields['initial_lc'].label = "Land Cover"
        except:
            pass

    class Meta:
        model = Parcel
        exclude = ('project',)

#Parcel_FormSet = inlineformset_factory(Project,Parcel, extra=2)


class ReferenceScenario_Form(BaseForm):
    def __init__(self, *args, **kwargs):
        super(ReferenceScenario_Form, self).__init__(*args, **kwargs)
        #try:
        self.fields['parcel'].queryset = Parcel.objects.filter(project=self.instance.project)
        #except:
        #    pass

    class Meta:
        model = Scenario
        exclude = ('project', 'landcovers', 'reference_scenario')

class UpdateProject_form(ModelForm):

    class Meta:
        model = Project
        include = ('cdm',)

class ProjectScenario_Form(BaseForm):
    def __init__(self, *args, **kwargs):
        super(ProjectScenario_Form, self).__init__(*args, **kwargs)
        #try:
        self.fields['reference_scenario'].queryset = Scenario.objects.filter(project=self.instance.project, reference_scenario__isnull=True)
        #except:
        #    pass

    class Meta:
        model = Scenario
        exclude = ('project', 'landcovers', 'parcel')


class LandUse_Form(BaseForm):

    def __init__(self, *args, **kwargs):
        super(LandUse_Form, self).__init__(*args, **kwargs)
        #print 'LandUse_Form kwargs = ',kwargs
        # Get project id from prefix
        projid = int(self.prefix.split('-')[0])
        project = Project.objects.get(id=projid)

        #print 'kwargs=',kwargs
        #print dir(self)
        #print dir(self.instance)
        #try:
        self.fields['practice'].queryset = Practice.objects.filter(project=project)
        self.fields['landcover'].queryset = LandCover.objects.filter(project=project)

        # Popup
        #self.fields['practice'].widget.url = project.geturl(Practice.get_newpu_urlname())
        #self.fields['landcover'].widget.url = project.geturl(LandCover.get_newpu_urlname())
        #except:
        #    pass
        #print 'self.instance',self.instance.scenario.name
        #print 'LandUse_Form'

    #    project = Project.objects.get(id=id)
        #print 'Project',project.name
    #    try:
    #        self.fields['landcover'].widget.url = project.geturl(LandCover.get_newpu_urlname())
    #        self.fields['practice'].widget.url = project.geturl(Practice.get_newpu_urlname())
    #    except:
    #        self.fields['landcover'].widget.url = ''
    #        self.fields['practice'].widget.url = ''
        #self.fields['practice'].widget.instance = self.instancepractice
        #print dir(self.instance)
        #print 'practice='
        #print 'scenario='
        #print dir(self.instance.scenario)
        # pass context data for custom widget
        #print 'practice_url=',self.instance.scenario.project.geturl_newpracticepu()
        #self.fields['practice'].widget.newpu_url = self.instance.scenario.project.geturl_newpracticepu()
        #scenario.project.geturl_newpracticepu()

    class Meta:
        model = LandUse
        exclude = ('scenario', 'adoption')


class LandUse_BaseFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        # CUSTOM FORMSET VALID #1:
        # Check that at least one of the inline Land Use forms has a start_year of 0 (or else our program logic breaks elsewhere)
        if not any(map(lambda form: form.cleaned_data.get('start_year', 1) == 0, self.forms)):
            raise ValidationError("At least one Land Cover must begin at year 0.")
        return super(LandUse_BaseFormSet, self).clean()

LandUse_FormSet = inlineformset_factory(Scenario, LandUse, extra=1, form=LandUse_Form, formset=LandUse_BaseFormSet, can_delete=True)

#class PrepopulateProjectForm(form.ModelForm):
#    class Meta:
#        model = Project
#        fields = ['soil_type','moisture_zone',
#        'climate_zone','continent',]