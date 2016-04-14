"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
For future programmmers, the third file to read to understand the mrv are the models.py files inside the sub project folders within the mrv. Each class in this
models files represent a table in the database. The most common used classes or tables are Plot, Parcel, Project, Tree, Project Boundary, Equation.  When a user upload 
excel with plot, parcel, and project informatiom the appropriate model create a row in the parcel, plolt, and project tables. Similarily, when a user create a point or polygon or upload a shape file that represents a parcel, plot, or polygon, the appropriate model create a row in the database for the appropriate table. Each class contains 
properties. If you want to use the properties of a model in your view or template, use django queries that returns model instead of raw data from the tables.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

from django.db import models
from django.contrib.auth.models import User
from mrvapi.models import *
from allometric import aeq
import mrvapi
import os
from django.utils import timezone
from django.db.models.loading import get_model
import datetime
from math import sqrt
from itertools import chain
from copy import deepcopy


class EquationCategory(models.Model):
    GENERAL = "G"
    CARBON_BENEFITS = "C"

    TYPE_CHOICES = (
        (GENERAL, "General"),
        (CARBON_BENEFITS,"Carbon Benefits")
        )

    STR_CHOICES = { key : value for (key,value) in TYPE_CHOICES }
    name = models.CharField(max_length=1, choices=TYPE_CHOICES)

    def __str__(self):
        return self.STR_CHOICES[self.name]


class EquationCountry(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    def __unicode__(self):
        return self.name

class EquationRegion(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    country = models.ForeignKey(EquationCountry, null=True) #each country has one or more regions, each region has multiple or more countries

    def __unicode__(self):
        return self.name

class EquationSpecies(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    genus = models.CharField(max_length=100, null=False, blank=False, default='')
    display = models.BooleanField(default=True)
    wood_gravity = models.FloatField(null=True, blank=True)
    region = models.ForeignKey(EquationRegion, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
            self.name = self.name.strip()
        self.genus = self.genus.lower()
        self.genus = self.genus.capitalize()
        self.genus = self.genus.strip()
        if self.name == '' or not self.name:
            self.display = False
        super(EquationSpecies, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s %s" % (self.genus, self.name)


class Equation(models.Model):
    SMALLWOOD = "SW"
    FOLIAGE = "FL"
    NULL = None
    ANATOMY_CHOICES = (
    	(NULL, '---'),
        (SMALLWOOD, 'Small Wood'),
        (FOLIAGE, 'Foliage')
        )
    STR_CHOICES = { key : value for (key,value) in ANATOMY_CHOICES }

    name = models.CharField(max_length=50, null=False, blank=False, help_text="e.g. Tropical moist forests (Brown 1997)")
    string = models.CharField(verbose_name='AGB Equation in kg DM', help_text="e.g. 42.69 - 12.8(dbh) + 1.242(dbh^2)", max_length=150, null=False, blank=False)
    owner = models.ForeignKey(User, null=False)
    #workgroup = models.BooleanField(verbose_name='shared with workgroup', help_text='Do you want to share this AEQ with your workgroup?')  # is it shared with group?
    public = models.BooleanField(verbose_name='public', help_text='Do you want to share this allometric equation with everyone?')  # is it public?
    species = models.ForeignKey(EquationSpecies, null=True, blank=True)
    region = models.ForeignKey(EquationRegion, null=True, blank=True)
    volumetric = models.BooleanField(default=False)
    default = models.BooleanField(default=False)
    #less_or_equal = models.BooleanField(default=False)
    less_than_ten = models.BooleanField(default=False)
    category = models.ForeignKey(EquationCategory, null=True) #each category has multiple equations
    anatomy = models.CharField(max_length=2, null=True, blank=True, choices=ANATOMY_CHOICES, default=None)
    latex = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        # unique_together = ('name',)
        pass

    def __unicode__(self):
        return self.name

    def _is_in_use(self):
        """ Returns true if any user's project/parcel/plot is currently using this AEQ """
        return self.project_set.count() + self.parcel_set.count() + self.plot_set.count() > 0
    is_in_use = property(_is_in_use)

    def _is_in_public_use(self):
        """ Returns true if a different user's project/parcel/plot is currently using this AEQ """
        return any(list(chain(self.plot_set.exclude(parcel__project__owner=self.owner), self.parcel_set.exclude(project__owner=self.owner), self.project_set.exclude(owner=self.owner))))
    is_in_public_use = property(_is_in_public_use)


    def clone(self, new_owner):
        """ Returns a copy of itself, with a new ID and new Owner """
        # Condition 1) We don't need to clone if we are already shared
        if self.public:
            return self
        # Condition 2) We don't need to clone if the user already has an identical AEQ they can use
        alternatives = get_model('allometric', 'Equation').objects.filter(name=self.name, string=self.string, owner=new_owner)
        if any(alternatives):
            return alternatives[0]

        # Case: User does not have access to the existing AEQ because of privacy
        clone = deepcopy(self)
        clone.id = None
        clone.owner = new_owner
        clone.save()  # This will create the clone and give it a new ID
        return clone

    def is_less_than_dbh(self, dbh):
        return dbh < 10.0

    def _sample_tree(self):
        ret = mrvapi.models.Tree()
        ret.dbh = 10
        ret.total_height = 2
        ret.crown_d_90 = 2
        ret.crown_d_max = 2
        ret.wood_gravity = 0.5
        return ret
    sample_tree = property(_sample_tree)

    def _sample_calculation_html(self):
        is_invalid = aeq.is_aeq_invalid(self.string)
        if is_invalid:
            return is_invalid

        expression, parameters, result = aeq.get_agb_result(self.string, self.sample_tree, verbose=True)
        return "<b>%s = %.2f</b><br>s.t. [%s]" % (expression, result, reduce(lambda x, y: "%s, %s" % (x, y), map(lambda x: "%s = %s" % (x, parameters[x]), parameters.keys())))
    sample_calculation_html = property(_sample_calculation_html)

    def _calculate_agb(self, tree):
        return aeq.get_agb_result(self.string, tree)
    calculate_agb = property(_calculate_agb)
