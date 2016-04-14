from django.conf.urls import patterns, url, include
#from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
#from core.views import *
from allometric.views import *


urlpatterns = patterns('',
	url(r'^$', GroupAEQ.as_view(), name='group_aeq'),
	url(r'^list/$', aeq_list),
	url(r'^add/$', CreateAEQ.as_view(), name='aeq_create'),
	url(r'^(?P<pk>\d+)/delete/confirm/$', DeleteAEQ.as_view(), name='aeq_delete_confirm'),
	url(r'^(?P<pk>\d+)/update/$', UpdateAEQ.as_view(), name='aeq_update'),
	url(r'^(?P<pk>\d+)/delete/$', 'allometric.views.deleteAEQ', name='delete_aeq'),
	url(r'^species/$', GroupSpecies.as_view(), name='species_list'),
	url(r'^species/list$', aeq_list),
	url(r'^species/add/$', CreateSpecies.as_view(), name='species_create'),
	url(r'^upload/$', UploadAEQ.as_view(), name='aeq_upload'),
	url(r'^upload/complete/$', 'allometric.views.uploadAEQ', name='aeq_upload_process'),
	)
