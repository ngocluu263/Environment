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
from tastypie import fields

# MRV Model Imports
from mrvapi.models import Project, Parcel, Plot
from .models import TreeAEQ
from allometric.models import *
import allometric.aeq


class ProjectCarbonResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        authentication = SessionAuthentication()
        authorization = Authorization()
        resource_name = "project-carbon"
        always_return_data = True
        fields = ['agb_tc', 'bgb_tc', 'soc_tc', 'litter_tc', 'deadwood_tc',
        'total_tc', 'total_area_used']

class ParcelCarbonResource(ModelResource):
    project = fields.ToOneField(ProjectCarbonResource, 'project', null=True)
    plots = fields.ToManyField('measuring.v1.PlotCarbonResource', 'plot_set', full=True, null=True)

    def dehydrate(self, bundle):
        bundle = super(ParcelCarbonResource, self).dehydrate(bundle)
        bundle.data['area'] = bundle.obj.area        
        bundle.data['total_tc_ha'] = bundle.obj.tc_ha_totals
        bundle.data['agb_tc'] = bundle.obj.agb_tc
        bundle.data['bgb_tc'] = bundle.obj.bgb_tc
        bundle.data['soc_tc'] = bundle.obj.soc_tc
        bundle.data['litter_tc'] = bundle.obj.litter_tc
        bundle.data['deadwood_tc'] = bundle.obj.deadwood_tc       
        return bundle              
        

    class Meta:
        queryset = Parcel.objects.all().order_by('name')
        authentication = SessionAuthentication()
        authorization = Authorization()
        resource_name = "parcel-carbon"
        always_return_data = True
        filtering = {'project' : ALL_WITH_RELATIONS}
        excludes = ['poly_mapped', 'post_resource_identifier', 'poly_mapped',
        'center_point', 'area_mapped', 'area_reported', 'hidden']

class PlotCarbonResource(ModelResource):
    project = fields.ToOneField('mrvapi.v1.ProjectResource', 'project')
    parcel = fields.ToOneField(ParcelCarbonResource, 'parcel', null=True)
    treeaeqs = fields.ToManyField('measuring.v1.TreeAEQResource', 'treeaeq_set', null=True)

    def dehydrate(self, bundle):
        bundle = super(PlotCarbonResource, self).dehydrate(bundle)
        bundle.data['area'] = bundle.obj.area
        bundle.data['total_tc_ha'] = bundle.obj.total_tc_ha
        bundle.data['root_shoot_ratio'] = bundle.obj.root_shoot_ratio
        equation = Equation.objects.get(id=bundle.obj.aeq_id)
        bundle.data['allometric_equation'] = equation.name
       #---------------------------------------------------------------------        
        #plot_carbon_stocks2 = bundle.obj._get_plot_carbon_stocks()
       # bundle.data['agb_tc_ha'] = plot_carbon_stocks2.agb_tc_ha
       #--------------------------------------------------------------------
        return bundle    

    class Meta:
        queryset = Plot.objects.all().order_by('name')
        authentication = SessionAuthentication()
        authorization = Authorization()
        resource_name = "plot-carbon"
        always_return_data = True
        filtering = {'project' : ALL_WITH_RELATIONS, 'parcel' : ALL_WITH_RELATIONS}
        fields = ['estimated_n_trees', 'trees_ha', 'dbh_mean', 'wsg_mean', 'height_mean', 'dbh_sd',
                'wsg_sd', 'height_sd', 'agb_tdm_ha', 'agb_tc_ha', 'bgb_tdm_ha', 'bgb_tc_ha',
                'soc_tc_ha', 'litter_tc_ha', 'deadwood_tc_ha', 'data_valid', 'id', 'project',
                'parcel', 'name']

class TreeAEQResource(ModelResource):
    tree = fields.ToOneField('mrvapi.v1.TreeResource', 'tree', full=True)
    aeq = fields.ToOneField('mrvapi.v1.AEQResource', 'aeq', full=True)
    plot = fields.ToOneField(PlotCarbonResource, 'plot', null=True)

    class Meta:
        queryset = TreeAEQ.objects.all()
        authentication = SessionAuthentication()
        authorization = Authorization()
        resource_name = "tree-aeq"
        always_return_data = True
        filtering = {'plot': ALL_WITH_RELATIONS}
        fields = ['tree', 'aeq', 'plot']
