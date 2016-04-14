from django.conf.urls import patterns, url, include
#from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from reports.views import *


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', ReportingView.as_view(), name='reporting'),
    url(r'^(?P<pk>\d+)/project_report/$', ProjectInfoReportView.as_view(), name='project_report'),
    url(r'^(?P<pk>\d+)/generate/$', 'reports.views.projectInfoReportView', name='proj_report'),
    # url(r'^(?P<pk>\d+)/mapping_report/$', '', name='mapping_report'),
    # url(r'^(?P<pk>\d+)/carbon_report/$', '', name='carbon_stocks_report'),
    )
