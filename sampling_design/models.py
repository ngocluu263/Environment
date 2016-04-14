"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
For future programmmers, the third file to read to understand the mrv are the models.py files inside the sub project folders within the mrv. Each class in this
models files represent a table in the database. The most common used classes or tables are Plot, Parcel, Project, Tree, Project Boundary, Equation.  When a user upload 
excel with plot, parcel, and project informatiom the appropriate model create a row in the parcel, plolt, and project tables. Similarily, when a user create a point or polygon or upload a shape file that represents a parcel, plot, or polygon, the appropriate model create a row in the database for the appropriate table. Each class contains 
properties. If you want to use the properties of a model in your view or template, use django queries that returns model instead of raw data from the tables.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from mrvapi.models import Project
#TESSTSTSTSTST
class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    mpoly = models.MultiPolygonField()
    objects = models.GeoManager()

    def _simple_mpoly(self):
        if self.mpoly_length > 500:
            return self.mpoly.simplify(tolerance=0.05)
        return self.mpoly
    simple_mpoly = property(_simple_mpoly)

    def _simple_mpoly_length(self):
        return self.simple_mpoly.num_points
    simple_mpoly_length = property(_simple_mpoly_length)

    def _mpoly_length(self):
        return self.mpoly.num_points
    mpoly_length = property(_mpoly_length)

    # Returns the string representation of the model.
    def __unicode__(self):
        return self.name


class GeoParcel(models.Model):
    name = models.CharField(max_length=50)
    mpoly = models.TextField(max_length=500)
    # mpoly = models.MultiPolygonField()
    project = models.ForeignKey(Project, related_name = 'sd_parcel_set', null=True)

    objects = models.GeoManager()

    # def _simple_mpoly(self):
    #     if self.mpoly_length > 500:
    #         return self.mpoly.simplify(tolerance=0.05)
    #     return self.mpoly
    # simple_mpoly = property(_simple_mpoly)

    # def _simple_mpoly_length(self):
    #     return self.simple_mpoly.num_points
    # simple_mpoly_length = property(_simple_mpoly_length)

    # def _mpoly_length(self):
    #     return self.mpoly.num_points
    # mpoly_length = property(_mpoly_length)

    # # Returns the string representation of the model.
    # def __unicode__(self):
    #     return self.name


class GeoPlot(models.Model):
    name = models.CharField(max_length=50)
    marker = models.PointField(null=True)
    parcel = models.ForeignKey(GeoParcel)

    objects = models.GeoManager()

