from django.conf.urls import patterns, url, include

from arcgis.views import *

urlpatterns = patterns('',
    url(r'^$', MappingIndex.as_view(), name='arcgis'),

    )