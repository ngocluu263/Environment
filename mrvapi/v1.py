"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
For future programmmers, the fourth group of  files to read to understand the mrv are V1.py in measuring, mapping, mrvapi, and sampling_designs foldeers. 
The classes in the v1.py files are web services. Each of the web service class queries a specific table in the database. One can identify the table by looking at the 
queryset under the class meta of the Class. The name of the webservice is also stored in the resource_name under the class meta. The url to these web services always 
contains the name of the web service. For example, the url    /api/v1/parcel/' + parcel_id + '/'    indicate that there is a parcel webservice or resource and you can 
get to it by passing parcel id. However, the url does not tell you which folder contains the parcel webservice or resources. So to find it you have to look into the 
V1.py files in measuring, mapping, mrvapi, and sampling_designs folders.  The hydrate and the dehydrate methods handle data going in and out of the webservice or resource.
The web services allow the Javascript portion of the mrv application to talk directly to the database without passing through the VIEW.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""


# tastypie imports
from tastypie.authentication import SessionAuthentication, Authentication, BasicAuthentication
from tastypie.authentication import *
from tastypie.authorization import Authorization, DjangoAuthorization, ReadOnlyAuthorization
from tastypie import fields
from tastypie.cache import SimpleCache
from tastypie.resources import ALL, ALL_WITH_RELATIONS, ModelResource
from tastypie.serializers import Serializer

# django imports
from django.contrib.auth.models import User
from django.db.models import Q
from v1auth import OwnerAuthorization, OwnerAuthorizationWithPublic

from itertools import chain

# project imports
from mrvapi.models import *
from ecalc.ipcc import *
from mrvapi.models import *
from allometric.models import *
from sampling_design.models import *
from mapping import *
from measuring.tasks import *
from celery.result import AsyncResult

# In general, the API should only be accessible from localhost to prevent CSRF attacks
#   I wrote the localhostSessionAuth class before to add some protection. However, in
#   development I am using plain SessionAuthentication and DjangoAuthorization.
#   I may need to roll my own Authorization class to use Django-Guardian or other object
#   level permissions.

# Here is a working example of how to add parent attributes to a child API call
    #def dehydrate(self, bundle):
    #    bundle.data['owner'] = bundle.obj.project.owner
    #    return bundle
# You can also often reference a parent object attributes using two underscores: parent__member
    #owner = fields.ToOneField(UserResource, 'project__owner')
# or
    #return object_list.filter(project__owner = request.user)

class MultipartResource(object):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencode':
            return request.post

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data
        return super(MultipartResource, self).deserialize(request, data, format)

    def put_detail(self, request, **kwargs):
        if request.META.get('CONTENT_TYPE').startswith('multipart') and not hasattr(request, '_body'):
            request._body = ''

        return super(MultipartResource, self).put_detail(request, **kwargs)

class localhostSessionAuthentication(SessionAuthentication):
    """ This is SessionAuthentication with localhost/127.0.0.1 whitelisted and others blocked """
    def is_authenticated(self, request, **kwargs):
        whitelist = ["localhost","127.0.0.1"]
        if request.META["SERVER_NAME"] in whitelist:
            return super(localhostSessionAuth, self).is_authenticated(request, **kwargs)
        return False


class UserResource(ModelResource):
    """ (read only) User resource used by other resources for reverse lookup """
    class Meta:
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'id', 'is_active', 'is_staff', 'is_superuser']
        allowed_methods = ['get']
        filtering = { 'username' : ALL, 'id' : ALL, }

class RegionResource(ModelResource):
    """ (read only) Region resource used in ASP form """
    class Meta:
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
        queryset = Region.objects.all()
        resource_name = 'region'
        allowed_methods = ['get']
        filtering = { 'name' : ALL, 'id' : ALL, }

class CountryResource(ModelResource):
    """ (read only) Country resource used in ASP form """
    region = fields.ToOneField(RegionResource, 'region', full=True)
    class Meta:
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
        queryset = Country.objects.all()
        resource_name = 'country'
        allowed_methods = ['get']
        filtering = {'region': ALL_WITH_RELATIONS, 'name' : ALL}

class AllometricCountryResource(ModelResource):
    class Meta:
        authentication = SessionAuthentication()
        authorization = Authorization()
        queryset = EquationCountry.objects.all()
        resource_name = 'allometric_country'
        allowed_methods = ['get']
        filtering = {'id': ALL, 'name': ALL}

class AllometricRegionResource(ModelResource):
    country = fields.ToOneField(AllometricCountryResource, 'country', full=True)
    class Meta:
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
        queryset = EquationRegion.objects.all()
        resource_name = 'allometric_region'
        allowed_methods = ['get']
        filtering = {'id': ALL, 'name': ALL, 'country': ALL_WITH_RELATIONS}

class AllometricSpeciesResource(ModelResource):
    class Meta:
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
        queryset = EquationSpecies.objects.all()
        resource_name = 'allometric_species'
        allowed_methods = ['get']
        filtering = {'id': ALL, 'name': ALL}


class ProjectResource(ModelResource):
    """ (remote) A user's projects """
    owner = fields.ToOneField(UserResource, 'owner')
    parcels = fields.ToManyField('mrvapi.v1.ParcelResource', 'parcel_set', null=True)
    projectboundaries = fields.ToManyField('mrvapi.v1.ProjectBoundaryResource', 'projectboundary_set', null=True, full=True)
    default_parcel = fields.ToOneField('mrvapi.v1.ParcelResourceWithHiddenNoPlots', 'default_parcel', null=True, full=False)  # MYD depends on full=False as it uses string URI
    default_parcel__id = fields.IntegerField('default_parcel__id', null=True)
    climate_zone = fields.CharField('climate_zone__name', null=True)
    moisture_zone = fields.CharField('moisture_zone__name', null=True)
    aeq = fields.ToOneField('mrvapi.v1.AEQResource', 'aeq', null=True)
    aeq__id = fields.IntegerField('aeq__id', null=True)
    projectpermissions = fields.ToManyField('mrvapi.v1.ProjectPermissionResource', 'projectpermissions_set', null=True)

    def dehydrate(self, bundle):
        bundle = super(ProjectResource, self).dehydrate(bundle)
        bundle.data['area_used'] = bundle.obj.area_used
        bundle.data['secret_code'] = bundle.obj.secret_code
        return bundle

    class Meta:
        queryset = Project.objects.all()
        #filtering = {'parcel' : ALL_WITH_RELATIONS}
        #filtering = {'cdm' : ALL_WITH_RELATIONS}
        resource_name = 'project'
        authentication = SessionAuthentication()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        serializer = Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'html', 'plist'])
        always_return_data = True

    def obj_create(self, bundle, **kwargs):
        return super(ProjectResource, self).obj_create(bundle, owner=bundle.request.owner)



class ProjectPermissionResource(ModelResource):
    project = fields.ToOneField(ProjectResource, 'project')
    user = fields.ToOneField(UserResource, 'user')
    class Meta:
        queryset = ProjectPermissions.objects.all()
        filtering = {'project': ALL_WITH_RELATIONS, 'user': ALL_WITH_RELATIONS }
        resource_name = 'projectpermissions'
        authentication = SessionAuthentication()
        authorization = Authorization()
        LIST_ALLOWED_METHODS = ['GET', 'delete']

    def obj_create(self, bundle, **kwargs):
        return super(ProjectPermissionResource, self).obj_create(bundle, user=bundle.request.user)


class DocumentsResource(MultipartResource, ModelResource):
    project = fields.ToOneField(ProjectResource, 'project')
    project__id = fields.IntegerField('project__id', null=True)
    parent_uri = fields.ToOneField('mrvapi.v1.DocumentsResource','parent', null=True)
    parent = fields.IntegerField('parent__id', null=True)

    class Meta:
        queryset = Documents.objects.all()
        filtering = {'project': ALL_WITH_RELATIONS}
        always_return_data = True
        resource_name = 'documents'
        authentication = SessionAuthentication()
        authorization = Authorization()
        list_allowed_methods = ['get','post','put','delete','patch']


# class UploadResource(ModelResource):
#     """ (remote) A project's uploads """
#     project = fields.ToOneField(ProjectResource, 'project')
#     project__id = fields.IntegerField('project__id', null=True)
#     folder = fields.ToOneField(UploadFolderResource, 'folder',null=True)
#     class Meta:
#         queryset = Upload.objects.all()
#         #parent = Project.objects.get(id=
#         filtering = {'project': ALL_WITH_RELATIONS}
#         resource_name = 'upload'
#         authentication = Authentication()
#         authorization = Authorization()
#         list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']

    # def obj_create(self, bundle, **kwargs):
    #     """ If a handle isn't provided I create one """
    #     bundle = super(UploadResource, self).obj_create(bundle, **kwargs)

    #     if bundle.obj.handle is None:
    #         handle = str(bundle.obj.project.id) + "_" + str(bundle.obj.id) + "_" \
    #             + str(bundle.obj.type) + "_" + str(bundle.obj.name)
    #         bundle.obj.handle = handle.replace(' ','-')
    #         bundle.obj.save()
    #     return bundle


class ProjectBoundaryResource(ModelResource):
    """ A project's parcels """
    project = fields.ToOneField(ProjectResource, 'project')
    project__id = fields.IntegerField('project__id', null=True)
    vertices_mapped = fields.CharField('vertices_mapped', null=True)
    vertices_reported = fields.CharField('vertices_reported', null=True)

    def hydrate_vertices_mapped(self, bundle):
        bundle = super(ProjectBoundaryResource, self).hydrate(bundle)
        bundle.obj.vertices_mapped = bundle.data['vertices_mapped']
        return bundle

    def hydrate_vertices_reported(self, bundle):
        bundle = super(ProjectBoundaryResource, self).hydrate(bundle)
        bundle.obj.vertices_reported = bundle.data['vertices_reported']
        return bundle
    def dehydrate(self, bundle):
        bundle = super(ProjectBoundaryResource, self).dehydrate(bundle)
        bundle.data['area_mapped'] = bundle.obj.area_mapped
        return bundle

    class Meta:
        queryset = ProjectBoundary.objects.all()
        #parent = Project.objects.get(id=
        filtering = {'project': ALL_WITH_RELATIONS}
        resource_name = 'projectboundary'
        authentication = SessionAuthentication()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        always_return_data = True

class ParcelResource(ModelResource):
    """ (remote) A project's parcels """
    project = fields.ToOneField(ProjectResource, 'project')
    project__id = fields.IntegerField('project__id', null=True)
    plots = fields.ToManyField('mrvapi.v1.PlotResource', 'plot_set', null=True)
    #owner = fields.ToOneField(UserResource, 'project__owner', null=True, full=True)
    aeq = fields.ToOneField('mrvapi.v1.AEQResource', 'aeq', null=True)
    aeq__id = fields.IntegerField('aeq__id', null=True)
    vertices_mapped = fields.CharField('vertices_mapped', null=True)
    vertices_reported = fields.CharField('vertices_reported', null=True)

    def hydrate_vertices_mapped(self, bundle):
        bundle = super(ParcelResource, self).hydrate(bundle)
        try:
            bundle.obj.vertices_mapped = bundle.data['vertices_mapped']
        except:
            pass
        return bundle

    def hydrate_vertices_reported(self, bundle):
        bundle = super(ParcelResource, self).hydrate(bundle)
        try:
            bundle.obj.vertices_reported = bundle.data['vertices_reported']
        except:
            pass
        return bundle  
     
    def dehydrate(self, bundle):
        bundle = super(ParcelResource, self).dehydrate(bundle)
        bundle.data['area_mapped'] = bundle.obj.area_mapped
        return bundle

    

    class Meta:
        queryset = Parcel.objects.all()
        #parent = Project.objects.get(id=
        filtering = {'project':ALL_WITH_RELATIONS, 'name':ALL, 'id': ALL}
        resource_name = 'parcel'
        authentication = SessionAuthentication()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        always_return_data = True


class PlotResource(ModelResource):
    """ (remote) A parcel's plots """
    # RELATIONS
    project = fields.ToOneField('mrvapi.v1.ProjectResource', 'project', null=True)
    parcel = fields.ToOneField('mrvapi.v1.ParcelResourceWithHiddenNoPlots', 'parcel', null=True)
    parcel__id = fields.IntegerField('parcel__id', null=True)
    parcel__project__id = fields.IntegerField('parcel__project__id', null=True)
    #owner = fields.ToOneField(UserResource, 'parcel__project__owner', full=True, null=True)
    trees = fields.ToManyField('mrvapi.v1.TreeResource', 'tree_set', null=True)
    aeq = fields.ToOneField('mrvapi.v1.AEQResource', 'aeq', null=True)
    aeq__id = fields.IntegerField('aeq__id', null=True)
    vertices_mapped = fields.CharField('vertices_mapped', null=True)
    vertices_reported = fields.CharField('vertices_reported', null=True)
    region = fields.ToOneField('mrvapi.v1.AllometricRegionResource','region', null=True)

    def hydrate_vertices_mapped(self, bundle):
        bundle = super(PlotResource, self).hydrate(bundle)
        try:
            bundle.obj.vertices_mapped = bundle.data['vertices_mapped']
        except:
            pass
        return bundle

    def hydrate_vertices_reported(self, bundle):
        bundle = super(PlotResource, self).hydrate(bundle)
        try:
            bundle.obj.vertices_reported = bundle.data['vertices_reported']
        except:
            pass
        return bundle  
    

    def dehydrate(self, bundle):
        bundle = super(PlotResource, self).dehydrate(bundle)
        bundle.data['area_mapped'] = bundle.obj.area_mapped
        return bundle

    def dehydrate(self, bundle):
        bundle = super(PlotResource, self).dehydrate(bundle)
        bundle.data['has_biomass_data'] = bundle.obj.has_biomass_data
        bundle.data['has_soil_data'] = bundle.obj.has_soil_data
        bundle.data['has_litter_data'] = bundle.obj.has_litter_data
        bundle.data['has_deadwood_data'] = bundle.obj.has_deadwood_data
        return bundle

    class Meta:
        queryset = Plot.objects.all().order_by('name')
        filtering = {'parcel' : ALL_WITH_RELATIONS, 'id':ALL, 'name': ALL, 'aeq': ALL_WITH_RELATIONS, 'trees': ALL_WITH_RELATIONS, 'project': ALL_WITH_RELATIONS}
        resource_name = 'plot'
        ordering = ['id', 'name']
        authentication = SessionAuthentication()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        always_return_data = True


class TreeResource(ModelResource):
    """ (remote) A plot's trees """
    plot = fields.ToOneField(PlotResource, 'plot')
    plot__id = fields.IntegerField('plot__id', null=True)
    plot__parcel__id = fields.IntegerField('plot__parcel__id', null=True)
    plot__parcel__project__id = fields.IntegerField('plot__parcel__project__id', null=True)

    class Meta:
        queryset = Tree.objects.all()
        filtering = {'plot' : ALL_WITH_RELATIONS}
        resource_name = 'tree'
        authentication = SessionAuthentication()
        authorization = Authorization()
        list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']


class AEQResource(ModelResource):
    species = fields.ToOneField(AllometricSpeciesResource, 'species', null=True, full=True)
    region = fields.ToOneField(AllometricRegionResource, 'region', null=True, full=True)
    class Meta:
        queryset = Equation.objects.all()
        resource_name = 'aeq'
        authentication = SessionAuthentication()
        authorization = Authorization()
        list_allowed_methods = ['get', 'delete']
        filtering = {'id': ALL, 'species': ALL_WITH_RELATIONS, 'region': ALL_WITH_RELATIONS}


class ParcelResourceWithHidden(ParcelResource):
    """ ALL+HIDDEN Parcel Resource with nested full Plot objects (instead of pointers) """
    plots = fields.ToManyField('mrvapi.v1.PlotResource', 'plot_set', null=True, full=True)
    class Meta(ParcelResource.Meta):
        queryset = Parcel.objects.all_with_hidden()
        resource_name = 'parcel-with-hidden'
        filtering = {'project': ALL_WITH_RELATIONS}

        cache = SimpleCache(timeout=10)  # used by plotParcel.aspx.vb


class ParcelResourceWithHiddenNoPlots(ParcelResource):
    """ ALL+HIDDEN Parcel Resource with no Plot objects (instead of pointers) """
    class Meta(ParcelResource.Meta):
        queryset = Parcel.objects.all_with_hidden()
        resource_name = 'parcel-with-hidden-no-plots'
        excludes = ['plots']

        cache = SimpleCache(timeout=60)  # used by savemapobjs2db.aspx.cs and plotParcel.aspx.vb


class VerboseProjectParcelResource(ProjectResource):
    """ Project Resource with nested full Parcel objects (instead of pointers) """
    parcels = fields.ToManyField('mrvapi.v1.ParcelResource', 'parcel_set', null=True, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'project-parcel'


class VerboseProjectParcelResourceWithHidden(ProjectResource):
    """ Project Resource with nested full Parcel objects (instead of pointers) """
    parcels = fields.ToManyField('mrvapi.v1.ParcelResourceWithHidden', 'parcel_set', null=True, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'project-parcel-with-hidden'


class VerboseProjectParcelResourceWithHiddenNoPlots(ProjectResource):
    """ Project Resource with nested full Parcel objects (instead of pointers) """
    parcels = fields.ToManyField('mrvapi.v1.ParcelResourceWithHiddenNoPlots', 'parcel_set', null=True, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'project-parcel-with-hidden-no-plots'

class VerboseProjectParcelPlotResource(ProjectResource):
    """ Project Resource with nested full Parcel/Plot objects (instead of pointers) """
    parcels = fields.ToManyField('mrvapi.v1.VerboseParcelPlotResource', 'parcel_set', null=True, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'project-parcel-plot'

class VerboseProjectParcelPlotResourceWithHidden(ProjectResource):
    """ Project Resource with nested full Parcel/Plot objects (instead of pointers) """
    parcels = fields.ToManyField('mrvapi.v1.ParcelResourceWithHidden', attribute=lambda bundle: Parcel.objects.all_with_hidden().filter(project=bundle.obj), null=True, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'project-parcel-plot-with-hidden'

class VerboseProjectParcelPlotTreeResource(ProjectResource):
    """ Project Resource with nested full Parcel/Plot/Tree objects (instead of pointers) """
    parcels = fields.ToManyField('mrvapi.v1.VerboseParcelPlotTreeResource', 'parcel_set', null=True, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'project-parcel-plot-tree'

class VerboseParcelPlotResource(ParcelResource):
    """ Parcel Resource with nested full Plot objects (instead of pointers) """
    plots = fields.ToManyField('mrvapi.v1.PlotResource', 'plot_set', null=True, full=True)
    class Meta(ParcelResource.Meta):
        resource_name = 'parcel-plot'

class VerboseParcelPlotResourceNoTrees(ParcelResource):
    """ Parcel Resource with nested full Plot objects (instead of pointers) """
    plots = fields.ToManyField('mrvapi.v1.PlotResourceNoTrees', 'plot_set', null=True, full=True)
    class Meta(ParcelResource.Meta):
        resource_name = 'parcel-plot-no-trees'

class VerboseParcelPlotTreeResource(ParcelResource):
    """ Parcel Resource with nested full Plot/Tree objects (instead of pointers) """
    plots = fields.ToManyField('mrvapi.v1.VerbosePlotTreeResource', 'plot_set', null=True, full=True)
    class Meta(ParcelResource.Meta):
        resource_name = 'parcel-plot-tree'

class PlotResourceNoTrees(PlotResource):
    """ Plot Resource with NO Tree objects"""
    trees = None
    class Meta(PlotResource.Meta):
        resource_name = 'plot-no-trees'

class VerbosePlotTreeResource(PlotResource):
    """ Plot Resource with nested full Tree objects (instead of pointers) """
    trees = fields.ToManyField('mrvapi.v1.TreeResource', 'tree_set', null=True, full=True)
    class Meta(PlotResource.Meta):
        resource_name = 'plot-tree'

class VerboseProjectProjectBoundaryResource(ProjectResource):
    """ Project Resource with nested full Parcel objects (instead of pointers) """
    projectboundaries = fields.ToManyField('mrvapi.v1.ProjectBoundaryResource', 'projectboundary_set', null=True, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'project-projectboundary'

class VerboseFullProjectResource(ProjectResource):
    """ Project Resource with computed cabon propeties & NESTED parcels """
    parcels = fields.ToManyField('mrvapi.v1.VerboseParcelPlotTreeResource', 'parcel_set', null=True, full=True)
    projectboundaries = fields.ToManyField('mrvapi.v1.ProjectBoundaryResource', 'projectboundary_set', null=True, full=True)
    default_parcel = fields.ToOneField('mrvapi.v1.ParcelResourceWithHidden', 'default_parcel', null=False, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'full-project'

class GeoProjectParcelPlotResource(ProjectResource):
    """ Project Resource with geographical information & NESTED parcels """
    parcels = fields.ToManyField('mrvapi.v1.GeoParcelPlotResource', 'parcel_set', null=True, full=True)
    default_parcel = fields.ToOneField('mrvapi.v1.GeoParcelPlotResource', 'default_parcel', null=False, full=True)
    projectboundaries = fields.ToManyField('mrvapi.v1.ProjectBoundaryResource', 'projectboundary_set', null=True, full=True)
    class Meta(ProjectResource.Meta):
        resource_name = 'geo-project-parcel-plot'

class GeoParcelPlotResource(ParcelResource):
    """ Parcel Resource with only geographical information and NESTED plots (instead of pointers) """
    plots = fields.ToManyField('mrvapi.v1.GeoPlotResource', 'plot_set', null=True, full=True)

    class Meta(ParcelResource.Meta):
        queryset = Parcel.objects.all_with_hidden()
        resource_name = 'geo-parcel-plot'
        excludes = []
        fields = ['name', 'area_mapped', 'vertices_mapped', 'area_reported', 'vertices_reported', 'id', 'resouce_uri']

class GeoPlotResource(PlotResource):
    """ Parcel Resource with only geographical information and NESTED plots (instead of pointers) """

    class Meta(PlotResource.Meta):
        resource_name = 'geo-plot'
        excludes = []
        fields = ['shape_reported', 'area_reported', 'dimensions_reported', 'utm_vertices_reported', 'vertices_reported',
                  'shape_mapped', 'area_mapped', 'dimensions_mapped', 'utm_vertices_mapped', 'vertices_mapped',
                  'name', 'id', 'parcel', 'parcel__id' ]

class CarbonStocksProjectResource(ProjectResource):
    """ Parcel resource with full computed carbon properties & NESTED plots """
    parcels = fields.ToManyField('mrvapi.v1.CarbonStocksParcelResource', 'parcel_set', full=True, null=True)
    # Climate moisture commented out, inherited from ProjectResuorce as *_zone
    # climate = fields.CharField('climate_zone__name', null=True)
    # moisture = fields.CharField('moisture_zone__name', null=True)

    def dehydrate(self, bundle):
        bundle = super(CarbonStocksProjectResource, self).dehydrate(bundle)
        # carbon_stocks are instantiated/computed when we access the property, and are therefore suited for dehydrate cycle
        carbon_stocks = bundle.obj.carbon_stocks  # We instantiate once here rather multiple property accesses during loop
        for fld in carbon_stocks._fields:
            bundle.data[fld] = getattr(carbon_stocks, fld)
        return bundle

    class Meta(ProjectResource.Meta):
        resource_name = 'project-carbon-stocks'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        fields = ['id', 'name', 'parcels', 'reported_area', 'region', 'moisture_zone', 'duration', 'climate_zone', 'country']

class CarbonStocksParcelResource(ParcelResource):
    """ Project resource with full computed carbon properties """
    plots = fields.ToManyField('mrvapi.v1.CarbonStocksPlotResource', 'plot_set', null=True, full=True)
    area_used = fields.FloatField('area')

    def dehydrate(self, bundle):
        bundle = super(CarbonStocksParcelResource, self).dehydrate(bundle)
        # carbon_stocks are instantiated/computed when we access the property, and are therefore suited for dehydrate cycle
        carbon_stocks = bundle.obj.carbon_stocks  # We instantiate once here rather multiple property accesses during loop
        for fld in carbon_stocks._fields:
            bundle.data[fld] = getattr(carbon_stocks, fld)
        return bundle

    class Meta(ParcelResource.Meta):
        resource_name = 'parcel-carbon-stocks'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        fields = ['id', 'area_used', 'project__id', 'name', 'plots']
        fields.extend(ParcelCarbonStocksStruct._fields)  # from mrvapi.models.py

class CarbonStocksParcelTierOneResource(ParcelResource):
    """ Parcel resource with full computed carbon properties with tier one data """
    def dehydrate(self, bundle):
        bundle = super(CarbonStocksParcelTierOneResource, self).dehydrate(bundle)

        carbon_stocks = bundle.obj.tier_one
        for fld in carbon_stocks._fields:
            bundle.data[fld] = getattr(carbon_stocks, fld)

        return bundle

    class Meta(ParcelResource.Meta):
        resource_name = 'parcel-carbon-stocks-t1'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        fields = ['id', 'area_used', 'project__id', 'name', 'plot']
        fields.extend(ParcelCarbonStocksStruct._fields)

class CarbonStocksParcelTierTwoResource(ParcelResource):
    """ Parcel resource with full computed carbon properties with tier one data """
    def dehydrate(self, bundle):
        bundle = super(CarbonStocksParcelTierTwoResource, self).dehydrate(bundle)

        carbon_stocks = bundle.obj.tier_two
        for fld in carbon_stocks._fields:
            bundle.data[fld] = getattr(carbon_stocks, fld)

        return bundle

    class Meta(ParcelResource.Meta):
        resource_name = 'parcel-carbon-stocks-t2'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        fields = ['id', 'area_used', 'project__id', 'name', 'plot']
        fields.extend(ParcelCarbonStocksStruct._fields)

class CarbonStocksPlotResource(PlotResource):
    """ Plot resource with full computed carbon properties """
    area_used = fields.FloatField('area')
    allometric_equation = fields.CharField('allometric_equation')

    def dehydrate(self, bundle):
        bundle = super(CarbonStocksPlotResource, self).dehydrate(bundle)
        # carbon_stocks are instantiated/computed when we access the property, and are therefore suited for dehydrate cycle
        carbon_stocks = bundle.obj.carbon_stocks  # We instantiate once here rather multiple property accesses during loop
        for fld in carbon_stocks._fields:
            bundle.data[fld] = getattr(carbon_stocks, fld)
        return bundle

    class Meta(PlotResource.Meta):
        resource_name = 'plot-carbon-stocks'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        fields = ['name', 'id', 'parcel__id', 'parcel__project__id', 'area_used', 'nontree_agb_tc_ha', 'nontree_bgb_tc_ha', 'allometric_equation', 'root_shoot_ratio']
        fields.extend(PlotCarbonStocksStruct._fields)  # from mrvapi.models.py


class PlotInformationASPXResource(PlotResource):
    """ Plot resource with full tree objects AND computed carbon properties (only used on PlotInformation.aspx.vb) """
    area_used = fields.FloatField('area')
    trees = fields.ToManyField('mrvapi.v1.TreeResource', 'tree_set', null=True, full=True)
    allometric_equation = fields.CharField('allometric_equation')

    def dehydrate(self, bundle):
        bundle = super(PlotInformationASPXResource, self).dehydrate(bundle)
        # carbon_stocks are instantiated/computed when we access the property, and are therefore suited for dehydrate cycle
        carbon_stocks = bundle.obj.carbon_stocks  # We instantiate once here rather multiple property accesses during loop
        for fld in carbon_stocks._fields:
            bundle.data[fld] = getattr(carbon_stocks, fld)
        return bundle

    class Meta(PlotResource.Meta):
        resource_name = 'plot-information'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        fields = ['name', 'id', 'parcel__id', 'parcel__project__id', 'area_used', 'allometric_equation', 'root_shoot_ratio',
                  'shape_mapped', 'shape_reported', 'vertices_mapped', 'vertices_reported', # this line used only for plotInformation.aspx
                  'dimensions_mapped', 'dimensions_reported', 'area_mapped', 'area_reported'] # this line used only for plotInformation.aspx
        fields.extend(PlotCarbonStocksStruct._fields)  # from mrvapi.models.py
