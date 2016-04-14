from django.conf.urls import patterns, url, include
#from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from mapping.views import *

urlpatterns = patterns('',
	url(r'^(?P<pk>\d+)/$', MappingView.as_view(), name="mapping-index"),
	url(r'^save/(?P<pk>\d+)/$', 'mapping.views.SaveMap', name="save-map"),
    url(r'^print/(?P<pk>\d+)/$', 'mapping.views.PrintMap', name='print-map')
	# url(r'^(?P<pk>\d+)/print/$', Print.as_view(), name="mapping-index-print")
	)