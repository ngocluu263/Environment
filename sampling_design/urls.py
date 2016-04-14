from django.conf.urls import patterns, url, include
from django.contrib.gis import admin

admin.autodiscover()

# Gets urls from mrvutils urls

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                      )