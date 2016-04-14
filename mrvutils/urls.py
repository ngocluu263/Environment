from django.conf.urls import patterns, url, include
#from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from mrvutils.views import LeakageEstimationTool, ProjectEmissionsTool, LEAKAGE_ESTIMATION_FORMS, PROJECT_EMISSIONS_FORMS
from sampling_design.views import SamplingDesignTool, SAMPLING_DESIGN_FORMS, PlotMappingTool

urlpatterns = patterns('',
                       # Soil Inventory Excel Sheet
                       url(r'^soilxls/(?P<project_id>\d+)/download/$', 'mrvutils.views.soil_xls_download', name='soil_xls_download'),
                       url(r'^soilxls/(?P<project_id>\d+)/upload/$', 'mrvutils.views.soil_xls_upload', name='soil_xls_upload'),
                       url(r'^shp2csv/(?P<project_id>\d+)/(?P<polygon_type>project|parcel|plot)/$', 'mrvutils.views.shp2csv', name='shp2csv'),
                       url(r'^leakage-estimation-tool/$', LeakageEstimationTool.as_view(LEAKAGE_ESTIMATION_FORMS), name='leakage-estimation-tool'),
                       url(r'^sampling-design-tool/$', SamplingDesignTool.as_view(SAMPLING_DESIGN_FORMS), name="sampling-design-tool"),
                       url(r'^plot-mapping-tool/$', PlotMappingTool.as_view(), name='plot-mapping-tool'),
                       url(r'^project-emissions-tool/$', ProjectEmissionsTool.as_view(PROJECT_EMISSIONS_FORMS), name='project-emissions-tool'),
                       url(r'^biomassxls/(?P<project_id>\d+)/upload/$', 'mrvutils.views.biomass_xls_upload', name='biomass_xls_upload'),
                       url(r'^coordinates/(?P<project_id>\d+)/type=(?P<polygon_type>project|parcel|plot)/$', 'mrvutils.views.polygonUpload', name="upload_coordinates"),
                       )
