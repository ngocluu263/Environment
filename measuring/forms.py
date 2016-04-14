from PIL import Image
from django import forms
from django.core.files.images import get_image_dimensions
from django.contrib.auth.models import User
import mrvapi.models
import ecalc.models
from ecalc.ipcc import *
from mrvapi.models import *
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist
import math

SHAPE_CHOICES=[('circle','circle'),
         ('rectangle','rectangle')]


MAX_IMAGE_SIZE = 600,600

class ModifyReportedAreaForm(forms.Form):
	reported_area_project = forms.FloatField(required = True)

	def clean(self):
		cleaned_data = super(ModifyReportedAreaForm, self).clean()

		reported = cleaned_data['reported_area_project']

		if math.isnan(reported):
			raise ValidationError('Must be a number')

		return cleaned_data

class ModifyParcelReportedAreaForm(forms.Form):
	parcelreportedarea = forms.FloatField(required = True)

	def clean(self):
		cleaned_data = super(ModifyParcelReportedAreaForm, self).clean()

		reported = cleaned_data['parcelreportedarea']

		if math.isnan(reported):
			raise ValidationError('Must be a number')

		return cleaned_data

class ModifyPlotInformationForm(forms.Form):
	shapeEdit = forms.ChoiceField(required = True, widget=forms.RadioSelect(), choices=SHAPE_CHOICES)
	radiusEdit = forms.FloatField(required = False)
	xDimEdit = forms.FloatField(required = False)
	yDimEdit = forms.FloatField(required = False)
	root_shoot_ratio = forms.FloatField(required=False)

	def clean(self):
		cleaned_data = super(ModifyPlotInformationForm, self).clean()
		return cleaned_data


class AddParcelForm(forms.Form):
	parcel_name = forms.CharField(max_length=50, required=True)
	parcel_area = forms.FloatField(required=True)

	def clean(self):
		cleaned_data = super(AddParcelForm, self).clean()

		area_to_clean = cleaned_data['parcel_area']

		if math.isnan(area_to_clean):
			raise ValidationError('Must be a number')

		return cleaned_data

class AddImageForm(forms.Form):
	image = forms.ImageField(label='Select an image')
	name = forms.CharField(required=True)

	def clean_image(self):
		image = self.cleaned_data.get('image')
		if image:
			if image._size > 2*1024*1024:
				raise ValidationError("Image file is too large. (>2MB")

			return image
		else:
			raise ValidationError("Couldn't read uploaded image")

class SaveParcelsPlotsForm(forms.Form):
	def clean(self):


		return cleaned_data