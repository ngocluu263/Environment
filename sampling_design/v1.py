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

from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.authentication import Authentication, SessionAuthentication
from sampling_design.models import WorldBorder, GeoParcel, GeoPlot
from tastypie.contrib.gis.resources import ModelResource, GeometryApiField
from tastypie.resources import Resource
from tastypie import fields
from mrvapi.v1 import OwnerAuthorization
from tastypie.resources import ALL, ALL_WITH_RELATIONS, ModelResource
from mrvapi.models import Project, Parcel, Plot

import random
from django.contrib.gis.geos import Point, Polygon


def get_random_point(extent):
    xrange = extent[2] - extent[0]
    yrange = extent[3] - extent[1]
    randx = xrange * random.random() + extent[0]
    randy = yrange * random.random() + extent[1]
    x = float(format(randx, '.4f'))
    y = float(format(randy, '.4f'))
    return Point(x, y)


class WorldBorderResource(ModelResource):
    simple_mpoly = GeometryApiField(attribute='simple_mpoly', null=True)
    simple_mpoly_length = fields.IntegerField(attribute='simple_mpoly_length', null=True)
    mpoly_length = fields.IntegerField(attribute='mpoly_length', null=True)

    class Meta:
        queryset = WorldBorder.objects.all()
        authorization = Authorization()
        authentication = Authentication()
        resource_name = 'worldborder'
        #exclude = ('mpoly',)
        excludes = ('mpoly',)
        always_return_data = True


from django.contrib.gis.geos import GEOSGeometry
import json
class ParcelResource(ModelResource):
    simple_mpoly = GeometryApiField(attribute='simple_mpoly', null=True)
    simple_mpoly_length = fields.IntegerField(attribute='simple_mpoly_length', null=True)
    mpoly_length = fields.IntegerField(attribute='mpoly_length', null=True)
    project = fields.ToOneField('mrvapi.v1.ProjectResource', 'project')

    class Meta:
        queryset = GeoParcel.objects.all()
        authorization = OwnerAuthorization('project__owner')
        authentication = Authentication()
        resource_name = 'geoparcel'
        filtering = {'project': ALL_WITH_RELATIONS}
        #exclude = ('mpoly',)
        excludes = ('mpoly',)
        always_return_data = True

    def full_hydrate(self, bundle):
        # log = open('out.txt', 'w')
        # log.write(str(json.dumps(bundle.data['mpoly'])))
        bundle.data['mpoly'] = GEOSGeometry(json.dumps(bundle.data['mpoly']))
        # log.write("\n\n")
        # log.write(str(bundle.data['mpoly']))
        # log.close()
        proj = Project.objects.get(id=bundle.request.session['project_id'])

        bundle.obj = Parcel(name=bundle.data['name'], mpoly=bundle.data['mpoly'], project=proj)
        return bundle


class PlotResource(ModelResource):
    parcel = fields.ToOneField('sampling_design.v1.ParcelResource', 'parcel')
    project = fields.ToOneField('mrvapi.v1.ProjectResource', 'parcel__project')

    class Meta:
        queryset = GeoPlot.objects.all()
        authorization = OwnerAuthorization('parcel__project__owner')
        authentication = Authentication()
        resource_name = 'geoplot'
        #exclude = ('mpoly',)
        #excludes = ('mpoly',)
        always_return_data = True
        filtering = {'project': ALL_WITH_RELATIONS}


class GenerateRandomPlotsResource(Resource):
    def obj_create(self, bundle, request=None, **kwargs):
        parcel = Parcel.objects.get(id=bundle.data['parcel'])

        if not bundle.data['distType']:
            count = int(bundle.data['count'])
            # Override) Generate random points
            # adapted http://djangodays.com/2009/03/04/geodjango-getting-a-random-point-within-a-multipolygon/
            extent = parcel.poly_mapped.extent
            plots = list()
            for i in range(1, count+1):
                pnt = get_random_point(extent)
                while not parcel.poly_mapped.contains(pnt):
                    pnt = get_random_point(extent)
                plt = Plot(name="plot_%s_%s" % (parcel.id, i), parcel=parcel, project=parcel.project, poly_mapped=Polygon([pnt, pnt, pnt, pnt]))
                plt.save()
                plots.append(plt)
        else:
            count = int(bundle.data['count'])
            n = int(bundle.data['nth'])
            extent = parcel.poly_mapped.extent
            x_range = extent[2] - extent[0]
            y_range = extent[3] - extent[1]

            col_len = x_range / int(bundle.data['cols'])
            row_len = y_range / int(bundle.data['rows'])

            last_x = extent[0]
            last_y = extent[3]
            plots = list()
            i = 0

            while i < count:
                if parcel.poly_mapped.contains(Point(last_x, last_y)):
                    pnt = Point(last_x, last_y)
                    plt = Plot(name="plot_%s_%s" % (parcel.id, i), parcel=parcel, project=parcel.project, poly_mapped=Polygon([pnt, pnt, pnt, pnt]))
                    plt.save()
                    plots.append(plt)
                    last_x += col_len * n
                    i += 1
                else:
                    if last_x > extent[2]:
                        last_x = extent[0]
                    else:
                        last_x += col_len * n
                        continue

                    last_y -= row_len

                    if last_y < extent[1]:
                        break

            # for i in range(0,count):
            #     if last_x + (col_len * n) <= extent[2]:
            #         last_x += col_len * n
            #         pnt = Point(last_x, last_y)
            #         p = Plot(name="plot_%s_%s" % (parcel.id, i), parcel=parcel, project=parcel.project, poly_mapped=Polygon([pnt, pnt, pnt, pnt]))
            #         p.save();
            #         plots.append(p)
            #     elif (last_x + (col_len * n)) > extent[2]:
            #         length_past_xmax = (last_x + (col_len * n)) - extent[2]
            #         if length_past_xmax > x_range:
            #             pass

            #         last_x = extent.xmin + length_past_xmax
            #         last_y -= row_len
            #         if last_y < extent[1]:
            #             break
            #         else:
            #             pnt = Point(last_x, last_y)
            #             p = Plot(name="plot_%s_%s" % (parcel.id, i), parcel=parcel, project=parcel.project, poly_mapped=Polygon([pnt, pnt, pnt, pnt]))
            #             p.save()
            #             plots.append(p)
        #bundle.obj = plots
        return bundle

    def get_resource_uri(self, updated_bundle):
        """ obj_create had been raising exception as it could not build a URI for the API resource """
        return ''

    class Meta:
        object_class = object
        authorization = Authorization()
        authentication = Authentication()
        resource_name = 'geogen'
        #exclude = ('mpoly',)
        #excludes = ('mpoly',)
        #always_return_data = True

class SamplingParcel(ModelResource):
    project = fields.ToOneField('mrvapi.v1.ProjectResource', 'project', null=True)
    poly_mapped = GeometryApiField(attribute='poly_mapped', null=True)
    poly_reported = GeometryApiField(attribute='poly_reported', null=True)
    center_point = GeometryApiField(attribute='center_point', null=True)

    def dehydrate(self, bundle):
        bundle = super(SamplingParcel, self).dehydrate(bundle);
        if bundle.obj.poly_mapped:
            bundle.data['center_point'] = bundle.obj.poly_mapped.centroid
        return bundle

    class Meta:
        queryset = Parcel.objects.all()
        fields = ['project', 'name', 'poly_mapped', 'poly_reported', 'id']
        authentication = SessionAuthentication()
        authorization = Authorization()
        resource_name = "parcel-sampling"
        always_return_data = True
        filtering = { 'project': ALL_WITH_RELATIONS }

class SamplingPlot(ModelResource):
    project = fields.ToOneField('mrvapi.v1.ProjectResource', 'parcel__project', null=True)
    parcel = fields.ToOneField(SamplingParcel, 'parcel', null=True)
    poly_mapped = GeometryApiField(attribute='poly_mapped', null=True)
    poly_reported = GeometryApiField(attribute='poly_reported', null=True)
    center_point = GeometryApiField(attribute='center_point', null=True)

    def dehydrate(self, bundle):
        bundle = super(SamplingPlot, self).dehydrate(bundle);
        if bundle.obj.poly_mapped:
            bundle.data['center_point'] = bundle.obj.poly_mapped.centroid
        return bundle

    class Meta:
        queryset = Plot.objects.all()
        fields = ['project', 'parcel', 'name', 'poly_mapped', 'poly_reported', 'id']
        authentication = SessionAuthentication()
        authorization = Authorization()
        resource_name = "plot-sampling"
        always_return_data = True
        filtering = { 'project': ALL_WITH_RELATIONS, 'parcel' : ALL_WITH_RELATIONS }
