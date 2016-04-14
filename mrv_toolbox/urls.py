
"""
---------------------------------------------------------------------------------------------------------------------------------
For future programmmers, the second file to read to understand the mrv is the main urls.py file located within the mrv_toolbox folder.  
This main url file recieve request and then redirect to the appropriate VIEW or WEB SERVICE through the url within the sub project folders
within the mrv.  All the api_v1.register with input name that ends with Resource are webservices.
The main urls also loads other urls within the sub project folders located in the mrv folder using the include syntax. So, after reading 
the main urls.py file, go to each folder within the mrv and read through the url files. This will help a lot in navigating the files in 
case of debugging.
-------------------------------------------------------------------------------------------------------------------------------------
"""

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
#from django.views.generic.simple import redirect_to  # DEPRECATED IN DJANGO 1.3, REMOVED THEREAFTER
from django.http import HttpResponsePermanentRedirect
from django.conf.urls import patterns, url, include
from django.conf import settings

# create redirect View for redirecting to ASP code
# (copied from deprecated/removed django.views.generic.simple.redirect_to)
def redirect_to(request, url, permanent=True, query_string=False, **kwargs):
    """
    Redirect to a given URL.

    The given url may contain dict-style string formatting, which will be
    interpolated against the params in the URL.  For example, to redirect from
    ``/foo/<id>/`` to ``/bar/<id>/``, you could use the following URLconf::

        urlpatterns = patterns('',
            ('^foo/(?P<id>\d+)/$', 'django.views.generic.simple.redirect_to', {'url' : '/bar/%(id)s/'}),
        )

    If the given url is ``None``, a HttpResponseGone (410) will be issued.

    If the ``permanent`` argument is False, then the response will have a 302
    HTTP status code. Otherwise, the status code will be 301.

    If the ``query_string`` argument is True, then the GET query string
    from the request is appended to the URL.

    """
    args = request.META["QUERY_STRING"]
    if args and query_string and url is not None:
        url = "%s?%s" % (url, args)

    if url is not None:
        klass = permanent and HttpResponsePermanentRedirect or HttpResponseRedirect
        return klass(url % kwargs)
    else:
        logger.warning('Gone: %s' % request.path,
                    extra={
                        'status_code': 410,
                        'request': request
                    })
        return HttpResponseGone()

# define api resources
# we are loading web services from the mrvapi folder
from tastypie.api import Api
import mrvapi.v1
import inspect
api_v1 = Api(api_name='v1')
# use inspect to add all classes from api as resouces
for x in dir(mrvapi.v1):
    obj = getattr(mrvapi.v1, x)  # x is a string, we must get the object
    if inspect.isclass(obj):
        try:
            api_v1.register(obj())  # we assume that the only class-type objects in models.py are in fact models
        except:
            pass  # we also nest it in a try/except statement to silently ignore any non-model classes which fail to register

# geo api resouces
# we are loading web services from the sampling_design, mappling, and measuring folder
import sampling_design.v1
import mapping.v1
import measuring.v1
#import arcgis.v1
api_v1.register(sampling_design.v1.WorldBorderResource())     # In the next 13 lines, we are registering web services  located in the sampling_design, mapping,      
api_v1.register(sampling_design.v1.ParcelResource())           # and  measuring folders that we can call in the urlpatterns below
api_v1.register(sampling_design.v1.PlotResource())
api_v1.register(sampling_design.v1.GenerateRandomPlotsResource())
api_v1.register(sampling_design.v1.SamplingParcel())
api_v1.register(sampling_design.v1.SamplingPlot())

api_v1.register(mapping.v1.MappingParcelResource())
api_v1.register(mapping.v1.MappingPlotResource())
api_v1.register(mapping.v1.MappingBoundaryResource())

api_v1.register(measuring.v1.ProjectCarbonResource())
api_v1.register(measuring.v1.ParcelCarbonResource())
api_v1.register(measuring.v1.PlotCarbonResource())
api_v1.register(measuring.v1.TreeAEQResource())



# v2 api resources
#from mobileapi import MOBILE_API_URL_ENDPOINT_PREFIX
#import mobileapi.v2
#api_v2 = Api(api_name=MOBILE_API_URL_ENDPOINT_PREFIX)
# use inspect to add all classes from api as resouces
#for x in dir(mobileapi.v2):
#    obj = getattr(mobileapi.v2, x)  # x is a string, we must get the object
#    if inspect.isclass(obj):
#        try:
#            api_v2.register(obj())  # we assume that the only class-type objects in models.py are in fact models
#        except:
#            pass  # we also nest it in a try/except statement to silently ignore any non-model classes which fail to register


admin.autodiscover()

from mrvutils.views import WOYPView
from measuring.tasks import getReCalculateCarbons

urlpatterns = patterns('',
                       # url(r'^$', TemplateView.as_view(template_name='base.html'), name='home'),
                       url(r'^$', redirect_to, {'url': '/cas/login/'}),
                       url(r'^favicon\.ico$', redirect_to, {'url': '/static/favicon.ico'}),
                       url(r'^robots\.txt$', redirect_to, {'url': '/static/robots.txt'}),
                       # including apps
                       url(r'^woyp/', WOYPView.as_view(), name='woyp-home'),
                       (r'^ecalc/', include('ecalc.urls')),            
                       (r'^mrvutils/', include('mrvutils.urls')),     
                       # enable the admin system
                       url(r'^admin/', include(admin.site.urls), name='admin'),
                       # enable cas!
                       url(r'^cas/', include('cas_provider.urls')),
                       # api resources
                       url(r'^api/', include(api_v1.urls)),
                       # core views
                       url(r'^core/', include('core.urls')),
                       #Smart Selects URl
                       # measuring urls
                       url(r'^measuring/', include('measuring.urls')),
                       url(r'^allometric/', include('allometric.urls')),
                       url(r'^mapping/', include('mapping.urls')),
                       url(r'^reports/', include('reports.urls')),
                       url(r'^arcgis/', include('arcgis.urls')),
                       url(r'^getReCalculateCarbon/$', getReCalculateCarbons),                      
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serving static files in development environment
#urlpatterns += staticfiles_urlpatterns()
