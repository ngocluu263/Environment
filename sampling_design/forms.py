from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from mrvapi.models import Project, Parcel
# Re-useable widgets
TEXTINPUT_5 = forms.TextInput(attrs={'size': '5'})
TEXTINPUT_10 = forms.TextInput(attrs={'size': '10'})
TEXTINPUT_15 = forms.TextInput(attrs={'size': '15'})
TEXTINPUT_20 = forms.TextInput(attrs={'size': '20'})
CHOICES_PERCENTAGES = map(lambda x: (x / 100.0, "%i%%" % x), range(0, 101))

class SamplingDesignForm1(forms.Form):
    level_of_error = forms.ChoiceField(choices=CHOICES_PERCENTAGES, initial=0.10)
    confidence_level = forms.ChoiceField(choices=[('90%', '90%'), ('95%', '95%'), ('99%', '99%')], initial='95%')
    # project_area_ha = forms.FloatField(label='Project Area', widget=TEXTINPUT_5)

class SamplingDesignForm(forms.Form):
    name = forms.CharField(label='Parcel Name', widget=TEXTINPUT_20)
    area_reported = forms.FloatField(label='Area (ha)', widget=TEXTINPUT_5)
    mean_total_tc_ha = forms.FloatField(label='Mean (tC/ha)', widget=TEXTINPUT_5)
    std_total_tc_ha = forms.FloatField(label='Standard Deviation (tC/ha)', widget=TEXTINPUT_5)
    plot_size_ha = forms.FloatField(label='Plot Size (ha)', widget=TEXTINPUT_5)

class SamplingDesignFormset(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(SamplingDesignFormset, self).__init__(*args, **kwargs)

        for form in self.forms:
            form.empty_permitted = False

    def clean(self):
        cleaned = super(SamplingDesignFormset, self).clean()

        # Don't bother validating the formset unless each form is valid on its own
        if any(self.errors):
            return cleaned

        # # Should be moved into strata step
        # if self.project_area_ha == 0:
        #     raise forms.ValidationError("Project area must be greater than zero.")

        # Validation 1) Make sure there is at least one Form passed
        if not self.forms:  # is our formset empty?
            raise forms.ValidationError('You must have at least one parcel.')

        # # Validation 2)
        # if not self.project_area_ha == reduce(lambda a, x: a + x.cleaned_data['area_ha'], self.forms, 0):
        #     raise forms.ValidationError('The sum of your parcel areas does not match your project area %d from step 1.'
        #         % ( self.project_area_ha ) )
        # return cleaned

SamplingDesignStrataFormset = formset_factory(SamplingDesignForm,
                                              extra=1,
                                              formset=SamplingDesignFormset)
