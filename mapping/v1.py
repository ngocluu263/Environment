
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
For future programmmers, the fourth group of  files to read to understand the mrv are V1.py in measuring, mapping, mrvapi, and sampling_designs foldeers. 
The classes in the v1.py files are web services. Each of the web service class queries a specific table in the database. One can identify the table by looking at the 
queryset under the class meta of the Class. The name of the webservice is also stored in the resource_name under the class meta. The url to these web services always 
contains the name of the web service. For example, the url    /api/v1/parcel/' + parcel_id + '/'    indicate that there is a parcel webservice or resource and you can 
get to it by passing parcel id. However, the url does not tell you which folder contains the parcel webservice or resources. So To find it you have to look into the 
V1.py files in measuring, mapping, mrvapi, and sampling_designs folders.  The hydrate and the dehydrate methods handle data going in and out of the webservice or resource.
The web services allow the Javascript portion of the mrv application to talk directly to the database without passing through the VIEW.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

# Tastypie Imports
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, SessionAuthentication
from tastypie.resources import ALL, ALL_WITH_RELATIONS

from tastypie.contrib.gis.resources import ModelResource, GeometryApiField
# from tastypie.resources import Resource # used in generating random plots
from tastypie import fields
# Project Imports
from mrvapi.v1 import OwnerAuthorization
from mrvapi.models import Project, ProjectBoundary, Parcel, Plot
from mrvapi.models import Project

class MappingBoundaryResource(ModelResource):
	project = fields.ToOneField('mrvapi.v1.ProjectResource', 'project', null=True)
	poly_mapped = GeometryApiField(attribute='poly_mapped', null=True)
	poly_reported = GeometryApiField(attribute='poly_reported', null=True)
	center_point = GeometryApiField(attribute='center_point', null=True)

	def dehydrate(self, bundle):
		bundle = super(MappingBoundaryResource, self).dehydrate(bundle)
		if bundle.obj.poly_mapped:
			if not bundle.obj.center_point:
				bundle.data['center_point'] = bundle.obj.poly_mapped.centroid
			bundle.data['area_mapped'] = bundle.obj.area_mapped

		return bundle

	class Meta:
		queryset = ProjectBoundary.objects.all()
		authentication = SessionAuthentication()
		authorization = Authorization()
		resource_name = "boundary-mapping"
		always_return_data = True
		filtering = { 'project': ALL_WITH_RELATIONS }


class MappingParcelResource(ModelResource):
	project = fields.ToOneField('mrvapi.v1.ProjectResource', 'project', null=True)
	poly_mapped = GeometryApiField(attribute='poly_mapped', null=True)
	poly_reported = GeometryApiField(attribute='poly_reported', null=True)
	center_point = GeometryApiField(attribute='center_point', null=True)

	def dehydrate(self, bundle):
		bundle = super(MappingParcelResource, self).dehydrate(bundle)
		if bundle.obj.poly_mapped:
			if not bundle.obj.center_point:
				bundle.data['center_point'] = bundle.obj.poly_mapped.centroid
			bundle.data['area_mapped'] = bundle.obj.area_mapped

		return bundle

	class Meta:
		queryset = Parcel.objects.all()
		authentication = SessionAuthentication()
		authorization = Authorization()
		resource_name = "parcel-mapping"
		always_return_data = True
		fields = ['id', 'project', 'name', 'poly_mapped', 'poly_reported', 'center_point', 'area_reported']
		filtering = { 'project': ALL_WITH_RELATIONS }

class MappingPlotResource(ModelResource):
	project = fields.ToOneField('mrvapi.v1.ProjectResource', 'parcel__project', null=True)
	parcel = fields.ToOneField(MappingParcelResource, 'parcel', null=True)
	poly_mapped = GeometryApiField(attribute='poly_mapped', null=True)
	poly_reported = GeometryApiField(attribute='poly_reported', null=True)
	center_point = GeometryApiField(attribute='center_point', null=True)

	def dehydrate(self, bundle):
		bundle = super(MappingPlotResource, self).dehydrate(bundle)
		if bundle.obj.poly_mapped and not bundle.obj.center_point:
			bundle.data['center_point'] = bundle.obj.poly_mapped.centroid
			bundle.data['area_mapped'] = bundle.obj.area_mapped
		return bundle

	class Meta:
		queryset = Plot.objects.all()
		authentication = SessionAuthentication()
		authorization = Authorization()
		resource_name = "plot-mapping"
		always_return_data = True
		fields = ['id', 'project', 'parcel', 'name', 'shape_mapped', 'shape_reported', 'dimensions_mapped', 'dimensions_reported', 'poly_mapped', 'poly_reported', 'area_reported']
		filtering = { 'project': ALL_WITH_RELATIONS, 'parcel': ALL_WITH_RELATIONS }

