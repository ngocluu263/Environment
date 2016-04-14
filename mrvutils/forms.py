from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory
from mrvapi.models import Project, Parcel
from ecalc.models import Biome
from ecalc.models import Parcel as Ecalc_Parcel
from django.forms import widgets


# Re-useable widgets
TEXTINPUT_5 = forms.TextInput(attrs={'size': '5'})
TEXTINPUT_10 = forms.TextInput(attrs={'size': '10'})
TEXTINPUT_15 = forms.TextInput(attrs={'size': '15'})
TEXTINPUT_20 = forms.TextInput(attrs={'size': '20'})
CHOICES_PERCENTAGES = map(lambda x: (x / 100.0, "%i%%" % x), range(0, 101))


class SoilXLSUploadForm(forms.Form):
    workbook = forms.FileField(label='Please select the Project Soil Data workbook after you have finished inputting soil data.',
                               help_text='')

class BiomassXLSUploadForm(forms.Form):
    workbook = forms.FileField()
    root_to_shoot = forms.FloatField(required=False)
    region = forms.IntegerField()
    equation = forms.IntegerField(required=False)

    def clean_root_to_shoot(self):
        root_shoot = self.cleaned_data['root_to_shoot']
        if not root_shoot:
            root_shoot = 0

        return root_shoot


class LeakageEstimationFormStep1(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.none(),
                                     help_text='Select the project you would like to compute emissions for.')
    forestland_fraction = forms.ChoiceField(choices=CHOICES_PERCENTAGES, initial=0.15)

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        super(LeakageEstimationFormStep1, self).__init__(*args, **kwargs)
        # Override 1) Filter the queryset for projects that belong to the owner
        self.fields['project'].queryset = Project.objects.filter(owner=self.owner)

class LeakageEstimationStratumForm(forms.ModelForm):
    area_pasture_ha = forms.FloatField(label='Area previously under pasture (ha)', widget=TEXTINPUT_10)
    beginning_tc_ha = forms.FloatField(label='Carbon density at beginning (tC/ha)', widget=TEXTINPUT_10)
    verification_tc_ha = forms.FloatField(label='Carbon density at verification (tC/ha)', widget=TEXTINPUT_10)

    class Meta:
        model = Parcel
        exclude = ('location', 'initial_lc')

    def __init__(self, *args, **kwargs):
        super(LeakageEstimationStratumForm, self).__init__(*args, **kwargs)
        # Override 1) Add instance attributes to form attributes for display in template
        self.stratum_name = self.instance.name
        self.stratum_area = self.instance.area
        # Override 2) Make certain fields use Hidden Widget
        self.fields['name'].widget = widgets.HiddenInput()
        self.fields['area'].widget = widgets.HiddenInput()

LeakageEstimationFormStep2 = inlineformset_factory(Project,
                                                   Ecalc_Parcel,
                                                   form=LeakageEstimationStratumForm,
                                                   can_delete=False,
                                                   extra=0)

#STEP 1
class SamplingDesignForm(forms.Form):
    level_of_error = forms.ChoiceField(choices=CHOICES_PERCENTAGES, initial=0.10)
    confidence_level = forms.ChoiceField(choices=[('90%', '90%'), ('95%', '95%'), ('99%', '99%')], initial='95%')
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        self.project_id = kwargs.pop('project_id')
        super(SamplingDesignForm, self).__init__(*args, **kwargs)

#STEP 2
class SamplingDesignStratumForm(forms.ModelForm):
    name = forms.CharField(label='Parcel Name', widget=TEXTINPUT_20)
    area_reported = forms.FloatField(label='Area (ha)', widget=TEXTINPUT_5)
    mean_tc_ha = forms.FloatField(label='Mean (tC/ha)', widget=TEXTINPUT_5)
    std_dev_tc_ha = forms.FloatField(label='Standard Deviation (tC/ha)', widget=TEXTINPUT_5)
    plot_size_ha = forms.FloatField(label='Plot Size (ha)', widget=TEXTINPUT_5)

    class Meta:
        model = Parcel
        exclude = ('project', 'post_resource_identifier', 'poly_mapped', 'poly_reported', 'aeq',
                   't1_agb', 't1_bgb', 't1_soc', 't1_deadwood', 't1_litter', 't2_agb', 't2_bgb', 't2_soc', 't2_deadwood',
                   't2_litter')

    def __init__(self, *args, **kwargs):
        super(SamplingDesignStratumForm, self).__init__(*args, **kwargs)
    def clean(self):
    	cleaned = super(SamplingDesignStratumForm, self).clean()
    	

# class SamplingDesignFormset(BaseFormSet):
#     def __init__(self, *args, **kwargs):
#         super(SamplingDesignFormset, self).__init__(*args, **kwargs)
#         for form in self.forms:
#             form.empty_permitted = False

#     def clean(self):
#         cleaned = super(SamplingDesignFormset, self).clean()

#         # Don't bother validating the formset unless each form is valid on its own
#         if any(self.errors):
#             return cleaned

#         # Validation 1) Make sure there is at least one Form passed
#         if not self.forms:  # is our formset empty?
#             raise forms.ValidationError('You must have at least one stratum.')

#         # # Validation 2)
#         # if not self.project_area_ha == reduce(lambda a, x: a + x.cleaned_data['area_ha'], self.forms, 0):
#         #     raise forms.ValidationError('The sum of your strata areas does not match your project area from step 1.')

#         return cleaned

SamplingDesignStrataFormset = inlineformset_factory(Project,
                                                    Parcel,
                                                    form=SamplingDesignStratumForm,
                                                    can_delete=True,
                                                    extra=1,
                                                    validate_max=False)


class ProjectEmissionsStratumForm(forms.Form):
    name = forms.CharField(label='Stratum Name', widget=TEXTINPUT_10)
    #area_ha = forms.FloatField(label='Area (ha)', widget=TEXTINPUT_5)
    area_burned_ha = forms.FloatField(label='Area burned (ha)', widget=TEXTINPUT_5)
    mean_agb_tdm_ha = forms.FloatField(label='Mean AGB at last verification (tDM/ha)', widget=TEXTINPUT_5)
    biome = forms.ModelChoiceField(queryset=Biome.objects.all(), label='Biome')


class ProjectEmissionsFormset(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(ProjectEmissionsFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

    def clean(self):
        cleaned = super(ProjectEmissionsFormset, self).clean()

        # Don't bother validating the formset unless each form is valid on its own
        if any(self.errors):
            return cleaned

        # Validation 1) Make sure there is at least one Form passed
        if not self.forms:  # is our formset empty?
            raise forms.ValidationError('You must have at least one stratum.')

        return cleaned

ProjectEmissionsStrataFormset = formset_factory(ProjectEmissionsStratumForm,
                                                extra=3,
                                                formset=ProjectEmissionsFormset)