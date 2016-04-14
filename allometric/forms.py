from django import forms
from django.contrib.auth.models import User
import allometric.models
from allometric.aeq import is_aeq_invalid
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist


class AEQUploadForm(forms.Form):
    aeqsheet = forms.FileField()

class SpeciesForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=False)
    genus = forms.CharField(max_length=100, required=True)
    wood_density = forms.FloatField(required=False)
    class Meta:
        model = allometric.models.EquationSpecies

class AEQForm(forms.ModelForm):
    genus = forms.CharField(max_length=100, required=False)
    species_text_field = forms.CharField(max_length=100, required=False)
    class Meta:
        model = allometric.models.Equation
        exclude = ['owner']

    def clean(self):
        cleaned_data = super(AEQForm, self).clean()
        string_expression = cleaned_data.get("string")

        # Validators
        if string_expression is None:
            string_expression = ''
        is_invalid = is_aeq_invalid(string_expression)
        if is_invalid:
            raise ValidationError(is_invalid)

        return cleaned_data