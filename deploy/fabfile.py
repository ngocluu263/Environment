'''
    Use this program to easily deploy the MRV to a separate server. This tool
    uses Fabric python package, so you will need to ensure fabric has been 
    installed through pip before you can run this program.
 
    This program will need SUDO access, as it needs to download a bunch of 
    packages, and make edits to the system for configuration.

    NOTE: This deployment package does not include enabling SSL. You will
    need to handle that yourself.

    Version: 0.1
    Created By: Brian Jurgess
'''

from fabric.api import hosts, run

APT_PACKAGES = [ 'git', 'python-pip', 'python-numpy', 'python-scipy', "python-software-properties", "build-essential", "apache2" "libapache2-mod-wsgi", "python-numpy", "python-scipy", "binutils", "libprojb-dev", "gdal-bin", "python-gdal", "python_lxml", "python_dateutil", "libblas-dev", "libblapack-dev", "gfortran", "python-dev", "libpq-dev",  "libpng12-0", "libpng12-dev"]
