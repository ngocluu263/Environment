"""
WSGI config for mrv_toolbox project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrv_toolbox.settings")

path='/var/www/mrv_toolbox'
if path not in sys.path:
    sys.path.append(path)
path2 = '/usr/lib/python2.7/dist-packages'
path3 = '/usr/local/lib/python2.7/dist-packages'
path4 = '/usr/local/lib/python2.7/site-packages'

if path2 not in sys.path:
    sys.path.append(path2)

if path3 not in sys.path:
    sys.path.append(path3)

if path4 not in sys.path:
    sys.path.append(path4)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
