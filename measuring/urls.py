from django.conf.urls import patterns, url, include
#from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
#from core.views import *
from measuring.views import *


urlpatterns = patterns('',
	url(r'^inventory_planning/(?P<pk>\d+)/$', InventoryPlanningView.as_view(), name='inventory-planning'),
	url(r'^data_management/(?P<pk>\d+)/$', DataManagementView.as_view(), name='data-management'),
	url(r'^carbon_calculations/(?P<pk>\d+)/$', CarbonCalculationsView.as_view(), name='carbon-calculations'),
	url(r'^parcel_management/(?P<pk>\d+)/$', ParcelManagementView.as_view(), name='parcel-management'),
	url(r'^parcel_management/edit_project_area/(?P<pk>\d+)/$', 'measuring.views.SubmitReportedArea', name='reported-area-project-form'),
	url(r'^parcel_management/edit_parcel_area/(?P<pk>\d+)/$', 'measuring.views.SubmitParcelReportedArea', name='reported-area-parcel-form'),
	url(r'^parcel_management/edit_plot_info/(?P<pk>\d+)/$', 'measuring.views.SubmitPlotInformation', name='parcel-information-form'),
	url(r'^parcel_management/add_parcel/(?P<pk>\d+)/$', 'measuring.views.AddParcel', name='add-parcel'),
	url(r'^parcel_management/plot_details/(?P<pk>\d+)/$', PlotDetailsView.as_view(), name='plot-details'),
	url(r'^parcel_management/add_plot/(?P<pk>\d+)/$', AddPlotView.as_view(), name='add-plot'),
	url(r'^data_management/plot_inventory/(?P<project_id>\d+)/(?P<pk>\d+)/$', PlotInventoryReview.as_view(), name="plot-inventory-review"),
	url(r'^delete_plot/(?P<pk>\d+)/$', 'measuring.views.deletePlot', name='delete-plot'),
	url(r'^manage_parcels_plots/(?P<pk>\d+)/$', ManageParcelsPlotsView.as_view(), name="manage-parcels-plots"),
	url(r'^manage_parcels_plots/save(?P<pk>\d+)/$', 'measuring.views.SaveParcelsPlots', name="save-parcels-plots"),
	url(r'^image_management/(?P<pk>\d+)/(?P<ppk>\d+)/upload/$', 'measuring.views.ImageUpload', name="upload-image"),
	url(r'^image_management/(?P<pk>\d+)/(?P<ppk>\d+)/upload/web/$', 'measuring.views.WebImageUpload', name="upload-image-web"),
	url(r'^image_management/(?P<pk>\d+)/(?P<ppk>\d+)/add/$', ImageUploadTest.as_view(), name='add-image'),
	url(r'^image_management/(?P<pk>\d+)/(?P<ppk>\d+)/$', ImagesView.as_view(), name='view-images'),
	url(r'^image_management/(?P<pk>\d+)/(?P<ppk>\d+)/(?P<pppk>\d+)/delete/$', 'measuring.views.ImageDelete', name='delete-image'),
	url(r'^image_management/(?P<pk>\d+)/view/$', ImageView.as_view(), name='view-image'),
    url(r'^data_management/upload/(?P<project_id>\d+)/$', 'measuring.views.MassDataUpload', name='parcel-data-upload'),
	url(r'^image_management/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media/'}),
	url(r'^recalculate/(?P<pk>\d+)/$', 'measuring.views.recalculate', name='carbon-recalculate')
	)
