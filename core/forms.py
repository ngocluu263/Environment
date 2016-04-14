from django import forms
from django.contrib.auth.models import User
import mrvapi.models
import ecalc.models
import allometric.models
from ecalc.ipcc import *
from mrvapi.models import *
from allometric.aeq import is_aeq_invalid
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist


class CopyProjectForm(forms.Form):
    secret_code = forms.CharField(label='Secret Code', required=True)

    def clean_secret_code(self):
        secret = self.cleaned_data['secret_code']
        secret = secret.strip()  # remove any erroneous whitespace from sloppy copy/paste

        # Validator 1) Refuse Null value
        if secret is None:
            raise ValidationError("You must enter a valid secret code.")

        # Validator 2) Refuse code without a match
        # Here, we also save the project instance to our form object for access in the view logic!
        try:
            self.project = mrvapi.models.Project.objects.get(secret=secret)
        except ObjectDoesNotExist:
            raise ValidationError("The secret code you entered did not match any project.")

        return secret


class AddUserProjectForm(forms.Form):
    USER_PERMISSION_LEVELS = (
            (0, 'Owner'),
            (1, 'Administrator'),
            (2, 'User'),
        )
    user_name = forms.CharField(label='Username', required=True)
    permission_level = forms.ChoiceField(choices=USER_PERMISSION_LEVELS, label='Permission Level')
    
    def clean_user_name(self):
        username = self.cleaned_data['user_name']
        username = username.strip()

        if username is None or username == '':
            raise ValidationError("You must enter a user name", code='invalid')

        try:
            self.user = User.objects.get(username = username)
        except ObjectDoesNotExist:
            raise ValidationError('The username you entered does not match any user', code='invalid')

        return username


class DocumentUploadForm(forms.Form):
    text = forms.CharField(max_length=50);
    upload = forms.FileField()


class AddUserForm(forms.ModelForm):
    clone_user = forms.ModelChoiceField(queryset=User.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'is_staff']

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)

        # Override #1 - We need to hash the password before saving
        new_user = super(AddUserForm, self).save(commit=False)
        new_user.set_password(self.cleaned_data["password"])

        # Save unless user passed kwarg commit=False
        if commit:
            new_user.save()  # Save at the top to get new PK ID used in override

            # Override #2 - We need to clone projects from passed clone_user field
            for project in mrvapi.models.Project.objects.filter(owner=self.cleaned_data['clone_user']):
                project.clone(new_user)  # New projects will be copied pointing at our new user id

        # Return new_user object like we are supposed to
        return new_user


class AEQForm(forms.ModelForm):
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


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = mrvapi.models.Project
        exclude = ['owner', 'region', 'country', 'type', 'secret', 'abstract',
                   'contact', 'email', 'telephone', 'address', 'address2', 'city',
                   'state', 'zipcode', 'country_address',
                   'reported_area', 'aeq', 'cdm', 'continent',
                   'climate_zone', 
                   'moisture_zone', 
                   'soil_type',
                   'duration', 'agb_tc', 'bgb_tc', 'soc_tc', 'litter_tc',
                   'deadwood_tc', 'total_tc', 'total_area_used', 'data_valid'
                   ]

class EditProjectForm(forms.ModelForm):
    region = forms.ModelChoiceField(queryset=Region.objects.all().order_by('name'), required=True)
    country = forms.ModelChoiceField(queryset=Country.objects.all().order_by('name'), required=True, widget=forms.Select(attrs={'disabled':'disabled'}))
    address2 = forms.CharField(required=False)
    continent = forms.ModelChoiceField(queryset=Continent.objects.all().order_by('name'), required=False)
    email = forms.EmailField(required=True, max_length = 50)
    #country_address = forms.ModelChoiceField(queryset=Country.objects.all(), required=True) #initial=Country.objects.filter(name__icontains=))

    class Meta:
        model = mrvapi.models.Project
        exclude = ['name','secret', 'aeq', 'cdm', 'name', 'reported_area','owner',
        'agb_tc', 'bgb_tc', 'soc_tc', 'litter_tc', 'deadwood_tc', 'total_tc', 'total_area_used',
        'data_valid']

class CreateParcelForm(forms.ModelForm):
    class Meta:
        model = mrvapi.models.Parcel
        fields = ['name', 'area_reported']

class CreateFolderForm(forms.Form):
    name = forms.CharField(required=False, max_length=30, widget=forms.TextInput(attrs={'placeholder':'Enter Folder Name'}))

    def clean(self):
        data = super(CreateFolderForm, self).clean()

        if not data.get('name'):
            data['name'] = 'New Folder'

        return data

    def clean_field(self):
        data = self.cleaned_data['name']
        if not data:
            data = 'New Folder'

        return data
