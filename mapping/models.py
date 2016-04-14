"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
For future programmmers, the third file to read to understand the mrv are the models.py files inside the sub project folders within the mrv. Each class in this
models files represent a table in the database. The most common used classes or tables are Plot, Parcel, Project, Tree, Project Boundary, Equation.  When a user upload 
excel with plot, parcel, and project informatiom the appropriate model create a row in the parcel, plolt, and project tables. Similarily, when a user create a point or polygon or upload a shape file that represents a parcel, plot, or polygon, the appropriate model create a row in the database for the appropriate table. Each class contains 
properties. If you want to use the properties of a model in your view or template, use django queries that returns model instead of raw data from the tables.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""



from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon, MultiPolygon, Point
from django.contrib.auth.models import User
from mrvapi.models import Project

class ProjectPolygonMapped(models.Model):
	""" for polygons that have a ptype of 'project' """
	project = models.ForeignKey(Project)
	name = models.CharField(max_length=50)
	poly_vertices = models.PolygonField()
	# area_mapped = models.FloatField(null=True, blank=True)
	# area_reported = models.FloatField(null=True, blank=True)
	objects = models.GeoManager()

	def __unicode__(self):
		return self.name

class ParcelPolygonMapped(models.Model):
	""" - for polygons that have a ptype of 'parcel'
		- the reason that this is seperate from project polygon is because there should be a relation
		to the mrvavi.parcel model.
		- area_mapped can be added here. / area_reported if it's apart of a defined parcel """

	project = models.ForeignKey(Project)
	name = models.CharField(max_length=50)
	poly_vertices = models.PolygonField()
	# area_mapped = models.FloatField(null=True, blank=True)
	# area_reported = models.FloatField(null=True, blank=True)
	objects = models.GeoManager()

	def __unicode__(self):
		return self.name

# save shapefile in a model
# class Shapefile(models.Model):
# 	project = models.ForeignKey(Project)
#	name = models.CharField(max_length=50)
#	json of shapefile.

class PointMapped(models.Model):
	""" - for anything on the map that uses a marker except the automatically drawn label for a polygon.
		- when sampling_type is blank then it's not a sampling_type
	"""
	project = models.ForeignKey(Project)
	name = models.CharField(max_length=50)
	pType = models.CharField(max_length=50)
	sampling_type = models.CharField(max_length=50, blank=True, default=None)
	marker = models.PointField()
	objects = models.GeoManager()

	def __unicode__(self):
		return self.name
