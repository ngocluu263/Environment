
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
For future programmmers, the third file to read to understand the mrv are the models.py files inside the sub project folders within the mrv. Each class in this
models files represent a table in the database. The most common used classes or tables are Plot, Parcel, Project, Tree, Project Boundary, Equation.  When a user upload 
excel with plot, parcel, and project informatiom the appropriate model create a row in the parcel, plolt, and project tables. Similarily, when a user create a point or polygon or upload a shape file that represents a parcel, plot, or polygon, the appropriate model create a row in the database for the appropriate table. Each class contains 
properties. If you want to use the properties of a model in your view or template, use django queries that returns model instead of raw data from the tables.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
#from django.db import models -- replaced with contrib.gis.db.models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon, MultiPolygon, Point
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from math import sqrt
from allometric import aeq
from allometric.models import EquationSpecies
import allometric
from copy import deepcopy
from itertools import chain
from django.db.models.loading import get_model
import numpy
import scipy.stats
import os
from django.core.exceptions import ObjectDoesNotExist
from shutil import copyfile
from mrv_toolbox.settings import IMAGES_FOLDER_PATH, DOCUMENTS_PATH
from mrv_toolbox.settings import BASE_DIR as PROJECT_HOME
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import RegexValidator
#from ecalc.ecalc import generate_default_land_covers
#import ecalc


class HiddenManager(models.Manager):
    # IMPORTANT: Inheriting from GeoManager breaks project creation ... beware. 2013/9/14
    """ This manager hides objects have have a hidden flag set """
    def get_query_set(self):
        return super(HiddenManager, self).get_query_set().filter(hidden=False)

    def all_with_hidden(self):
        return super(HiddenManager, self).get_query_set()

    def hidden_set(self):
        return super(HiddenManager, self).get_query_set().filter(hidden=True)


def average(ls):
    try:
        return sum(ls) * 1.0 / len(ls)
    except ZeroDivisionError:
        return 0.0


def from_string_vertices_to_gis_polygon(vertices_string):
    vertices_list = vertices_string.split(',')
    vertices_list_as_floats = map(lambda x: float(x), vertices_list)
    lats = vertices_list_as_floats[::2]
    lngs = vertices_list_as_floats[1::2]
    coords = zip(lats, lngs)

    ret_coords = coords
    while len(coords) < 4:
        ret_coords.append(coords[-1])

    if ret_coords[0] != ret_coords[-1]:
        ret_coords.append(ret_coords[0]);
    return Polygon(ret_coords)



def polygon_to_unicode_vertices_string(poly):
    return unicode(''.join(char for char in str(poly.coords[0]) if char in '0123456789.,-'))


class Region(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Country(models.Model):
    region = models.ForeignKey(Region)
    name = models.CharField(max_length=50)
    #continent = models.ForeignKey('ecalc.Continent', null=True);

    def __unicode__(self):
        return self.name


class ProjectCarbonStocksStruct():
    _fields = ['agb_tc',
               'bgb_tc',
               'soc_tc',
               'litter_tc',
               'deadwood_tc',
               'total_tc',
               'total_parcel_area'
               ]

    def __init__(self):
        for fld in self._fields:
            setattr(self, fld, 0.0)


class Project(models.Model):
    #alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
    owner = models.ForeignKey(User) #related_name="Owner"
    name = models.CharField(max_length=100, null=True, )  # TODO: add blank=False, choices=???, to this and other fields
    region = models.CharField(max_length=50, null=True)  # TODO: remove Null allow after i finish migrating? or will this only break the API if blanks not validated in ASP?
    country = models.CharField(max_length=50, null=True)

    ## Remove the comment around this when we migrate
    #country_key = models.ForeignKey(Country, null=True)

    type = models.CharField(max_length=50, null=True)
    #method call = 4545
    secret = models.CharField(max_length=50, null=True, blank=True)  # Secret code used for sharing projects -- should be accessed through _secret_code method
    abstract = models.TextField(null=True)
    contact = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=50, null=True)
    telephone = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=50, null=True)
    address2 = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    zipcode = models.CharField(max_length=15, null=True)
    country_address = models.CharField(max_length=50, null=True)
    duration = models.IntegerField("Duration (yrs)", null=True,blank=True)
    reported_area = models.FloatField(null=True, blank=True)  # TODO :consider using DecimalField(max_digits=15, decimal_places=4)
    #aeq = models.ForeignKey('Allometric_Equation', null=True)  # this can be null, in which case the get_aeq() method returns a default
    aeq = models.ForeignKey('allometric.Equation',null=True)
    # ECALC IPCC defaults for loading land cover types
    continent = models.ForeignKey('ecalc.Continent', null=True)
    climate_zone = models.ForeignKey('ecalc.Climate_Zone', null=True)
    moisture_zone = models.ForeignKey('ecalc.Moisture_Zone', null=True)
    soil_type = models.ForeignKey('ecalc.Soil_Type', null=True)
    # ECALC constants
    cdm = models.FloatField("Carbon/Dry Matter ratio", default=0.47)

    agb_tc          = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    bgb_tc          = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    soc_tc          = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    litter_tc       = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    deadwood_tc     = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    total_tc        = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    total_area_used = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)

    # Determines if the data is valid or not. False, data must be
    # recalculated. True, data is valid.
    data_valid      = models.BooleanField(default=False)

    _original_climate_zone = None
    _original_moisture_zone = None
    _original_soil_type = None
    _original_duration = None
    _original_region = None
    _original_country = None

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self._original_moisture_zone = self.moisture_zone
        self._original_soil_type = self.soil_type
        self._original_climate_zone = self.climate_zone
        self._original_duration = self.duration
        self._original_country = self.country
        self._original_region = self.region

    def _default_parcel(self):
        """ Return the default parcel (which is Hidden and not viewable in parcel_set) """
        try:
            return Parcel.objects.all_with_hidden().get(project=self, hidden=True)  # There should only ever be 1 so this is an exact get()
        except:
            # There is a corner-case where the default_parcel hasn't been created yet.
            # An app may try to do things with a newly created Project before it has been saved for the first time
            # And unfortunately, we can't just create it here as the project.pk doesn't exist until project is saved
            # ... in which case it will have the hidden parcel next time around :)
            return None
    default_parcel = property(_default_parcel, lambda x, y: True)  # Always return a no-op True on __setatr__

    def _secret_code(self):
        """ Return the secret if it exists, else generate it and return that """
        return self.secret if self.secret is not None else self.reset_secret_code()
    secret_code = property(_secret_code)

    def reset_secret_code(self):
        """ Generates a new secret code hash that is UNIQUE, saves it, and returns it """
        while True:
            """ Loop until we generate a unique hash """
            secret_hash = os.urandom(8).encode('hex')  # 16 characters long
            try:
                Project.objects.get(secret=secret_hash)
            except ObjectDoesNotExist:
                break  # if the object does not exist, we have a unique key!
        self.secret = secret_hash
        self.save()
        return secret_hash

    def get_aeq(self):
        return self.aeq or get_model('mrvapi', 'Allometric_Equation').objects.get(pk=1)

    def _area_used(self):
        return self.reported_area
    area_used = property(_area_used)

    # #will create a new project
    # #copy all the attributes other than the ID to new project
    # #pass back object to newclone function

    # def clone(self,new_owner,new_name=""):
    #     """ Returns a copy of itself, with a new ID and new FK parent, and with all new copied children """
    #     clone = deepcopy(self)
    #     clone.id = None
    #     clone.owner = new_owner
    #     if new_name == "":
    #         new_name = self.name
    #     clone.name = new_name
    #     clone.save(clone=True)  # This will create the clone and give it a new ID
    #     clone.reset_secret_code()  # special case 1: we need to generate a unique secret key for the project
    #     return clone


    def clone(self, new_owner, new_name=""):
        """ Returns a copy of itself, with a new ID and new FK parent, and with all new copied children """
        clone = deepcopy(self)
        clone.id = None
        clone.owner = new_owner
        if new_name == "":
            new_name = self.name
        clone.name = new_name
        clone.save(clone=True)  # This will create the clone and give it a new ID
        clone.reset_secret_code()  # special case 1: we need to generate a unique secret key for the project

        # special case: we need to clone the default_parcel (done before other parcels to preserve ordering in dropdown menus)
        # self.default_parcel.clone(clone)
        self.default_parcel.clone_children(clone, clone.default_parcel)

        # Permissions
        self.mainProjectPermission = ProjectPermissions.objects.get(project = self.id, user=self.owner)
        self.mainProjectPermission.clone(clone)

        # Next, we need to iterate through descendant objects and give them our new PK by calling .clone(PK)
        # Note that parcel_set() excludes the hidden default_parcel, so we are good and aren't doing that one twice
        children = list(chain(self.parcel_set.all(), self.projectboundary_set.all()))
        for child in children:
            child.clone(clone)  # This calls the children clone function with our new clone ID as parent

        # Create a new AEQ
        if self.aeq:
            clone.aeq = self.aeq.clone(clone.owner)

        # ECALC relations cloning
        # Next, we need to iterate through descendant objects and give them our new PK by calling .clone(PK)
        delta_dict = dict()  # delta_dict is mutable, and gets the new Object/FK relation ids keyed by old {(obj.__class__.__doc__, old_id): new_id
        delta_dict[(self.__doc__, self.id)] = clone.id


        # children = list(chain( self.practice_set.all(), self.landcover_set.all(),
        #                         self.scenario_set.filter(reference_scenario=None), self.scenario_set.filter(reference_scenario=True),
        #                         self.ecalc_parcel_set.all(),
        #                         # it is important that you do reference scenarios first, i.e. ref=None (not a proj scen)
        #                         # self.scenario_set.filter(reference_scenario=True) ---> project scenarios? or at least an attempt
        #                       ))


        children = list(chain( self.practice_set.all(), self.landcover_set.all(),self.ecalc_parcel_set.all(),
                                self.scenario_set.filter(reference_scenario=None),
                                # it is important that you do reference scenarios first, i.e. ref=None (not a proj scen)
                                # self.scenario_set.filter(reference_scenario=True) ---> project scenarios? or at least an attempt
                              ))

        for child in children:
            child.clone(delta_dict)

        children1 = list(chain(self.scenario_set.all()))
        childtest1 = (children1[0].__doc__, children1[0].id)

        #raise Exception("Test - list")
        for child in children1:
            if (child.__doc__, child.id) in delta_dict:
                pass
            else:
                child.clone(delta_dict)

        # finally, save the clone
        clone.save()

        return clone

    # @ECALC
    def Climate(self):
        if self.climate_zone != None and self.moisture_zone != None:
            return get_model('ecalc', 'Climate').objects.get(climate_zone=self.climate_zone, moisture_zone=self.moisture_zone)
        return get_model('ecalc', 'Climate').objects.get(climate_zone=1, moisture_zone=1)

    # @ECALC
    def SClimate(self):
        return self.Climate().simple_climate
    # @ECALC
    @property
    def gwp_ch4(self):
        return 25.0  # get from tables
    # @ECALC
    @property
    def gwp_n2o(self):
        return 298.0 # get from tables
    # @ECALC
    @models.permalink
    def get_absolute_url(self):
        return('ecalc-project',[str(self.id)])
    # @ECALC
    @models.permalink
    def geturl(self,urlname):
        return(urlname,[str(self.id),])
    # @ECALC
    def __unicode__(self):
        return self.name

    def _get_project_carbon_stocks(self):
        # Create struct
        ret = ProjectCarbonStocksStruct()

        for parcel in Parcel.objects.filter(project=self):
            parcel_carbon_stocks = parcel.carbon_stocks  # only call accessor once, as its a property function
            ret.agb_tc += parcel_carbon_stocks.agb_tc
            ret.bgb_tc += parcel_carbon_stocks.bgb_tc
            ret.soc_tc += parcel_carbon_stocks.soc_tc
            ret.litter_tc += parcel_carbon_stocks.litter_tc
            ret.deadwood_tc += parcel_carbon_stocks.deadwood_tc
            ret.total_tc += parcel_carbon_stocks.total_tc
            ret.total_parcel_area += parcel_carbon_stocks.area_used

        return ret

    carbon_stocks = property(_get_project_carbon_stocks)

    # Create a dummy/default parcel when you create a project to store orphan plots
    def save(self, *args, **kwargs):

        # if we have a clone, we've also cloned the default parcel and do not need to make another one!
        clone_boolean = kwargs.pop('clone', False)

        if not self.aeq:
            self.aeq = allometric.models.Equation.objects.get(id=1)
        if not self.pk:
            # This code only happens if the objects is not in the database yet, on the first save. Otherwise it would have pk
            if not clone_boolean:
                # STEP 1 - Create Hidden Parcel for storing orphan plots
                super(Project, self).save(*args, **kwargs)
                hidden_parcel = Parcel.objects.create(project_id=self.pk, name="-- No Parcel --", hidden=True)
                hidden_parcel.save()
                # Explanation: because of the custom Manager (HiddenManager), this parcel will
                # be omitted from most project reporting and is therefore a useful
                # container for orphan plots (those with no parcel selected .. yet)

                # STEP 2 - Generate IPCC Land Covers
                if Project.climate_zone is not None:
                    self._generate_default_land_covers()
        else:
            if (self.climate_zone != self._original_climate_zone) or (self.moisture_zone != self._original_moisture_zone) or\
             (self.soil_type != self._original_soil_type) or (self.duration != self._original_duration) or (self.country != self._original_country) or (self.region != self._original_region):
                self._generate_default_land_covers()
            super(Project, self).save(*args, **kwargs)
            self._original_duration = self.duration
            self._original_soil_type = self.soil_type
            self._original_climate_zone = self.climate_zone
            self._original_moisture_zone = self.moisture_zone
            self._original_region = self.region
            self._original_country = self.country

    #@receiver(post_save, sender=User)
    #def postSave(self, *args, **kwargs):
     #   if (self.climate_zone != self._original_climate_zone) or (self.moisture_zone != self._original_moisture_zone) or\
      #  (self.soil_type != self._original_soil_type) or (self.duration != self._original_duration) or\
       #  (self.country != self._original_country) or (self.region != self._original_region):
        #    self._generate_default_land_covers()



    def _generate_default_land_covers(self):
        project = self
        climate = project.Climate()
        currentLandcovers = get_model('ecalc', 'LandCover').objects.filter(project=project)
        currentPractices = get_model('ecalc', 'Practice').objects.filter(project=project)
        if currentLandcovers is not None:
            currentLandcovers.delete()
        if currentPractices is not None:
            currentPractices.delete()

        necromass = get_model('ecalc', 'Necromass').objects.get(climate=climate)
        if project.soil_type != None:
            soil_carbon = get_model('ecalc', 'Soil_Carbon_Ref').objects.get(soil_type=project.soil_type, climate=climate)
        else:
            soil_carbon = get_model('ecalc', 'Soil_Carbon_Ref').objects.get(soil_type=1, climate=climate)
        biomes = get_model('ecalc', 'Biome').objects.filter(climate_zone=project.climate_zone)
        land_use = get_model('ecalc', 'Land_Use').objects.get(name='Forest')
        # Load forests
        for i, biome in enumerate(biomes):
            belowgroundRatios = get_model('ecalc', 'Belowground_Ratio').objects.filter(biome=biome)
            combustionFactor = get_model('ecalc', 'Combustion_Factor').objects.get(biome=biome)
            for managed in (False, True):
                aboveground_biomass = get_model('ecalc', 'Aboveground_Biomass').objects.get(continent=project.continent, managed=managed, biome=biome)
                # to get belowground multiply aboveground by belowground ratio
                for belowgroundRatio in belowgroundRatios:
                    category = belowgroundRatio.category
                    abovegroundLimit = float(category[1:])
                    if aboveground_biomass.value < abovegroundLimit: break
                    belowgroundRatio_value = belowgroundRatio.value
                old_growth_rate = get_model('ecalc', 'Forest_Growth').objects.get(managed=managed,continent=project.continent,biome=biome,youngOrOld='O')
                young_growth_rate = get_model('ecalc', 'Forest_Growth').objects.get(managed=managed,continent=project.continent,biome=biome,youngOrOld='Y')
                name = project.continent.name+" "+biome.name
                if managed: name = name+" (plantation)"
                soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
                get_model('ecalc', 'LandCover')(name=name, project = project,category='F',
                    biomassa = aboveground_biomass.value, biomassb = aboveground_biomass.value*belowgroundRatio_value,
                    litter = necromass.litterC, dead_wood = necromass.deadwoodC, soil = soil_carbon.value * soil_carbon_factor.value,
                    combustion_pctreleased = combustionFactor.pctReleased,
                    CH4 = combustionFactor.emissCH4, N2O = combustionFactor.emissN2O,
                    old_growth_rate = old_growth_rate.value, young_growth_rate = young_growth_rate.value,
                    biomassratio = belowgroundRatio_value).save()
        # Load one of each other type
        nfactor = 2.0 * project.cdm

        land_use = get_model('ecalc', 'Land_Use').objects.get(name='Annual Crop')
        soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
        biomass = get_model('ecalc', 'Biomass_Land_Use').objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
        CF = get_model('ecalc', 'Combustion_Land_Use').objects.get(land_use=land_use)
        get_model('ecalc', 'LandCover')(name=land_use.name, project=project, category='A',
                  biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
                  combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

        land_use = get_model('ecalc', 'Land_Use').objects.get(name='Perennial/Tree Crop')
        CF = (get_model('ecalc', 'Combustion_Land_Use').objects.filter(land_use=land_use))[0]
        soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
        biomass = get_model('ecalc', 'Biomass_Land_Use').objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
        get_model('ecalc', 'LandCover')(name=land_use.name, project=project, category='P',
                  biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
                  combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

        land_use = get_model('ecalc', 'Land_Use').objects.get(name='Paddy Rice')
        soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
        biomass = get_model('ecalc', 'Biomass_Land_Use').objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
        CF = get_model('ecalc', 'Combustion_Land_Use').objects.get(land_use=land_use)
        get_model('ecalc', 'LandCover')(name=land_use.name, project=project, category='R',
                  biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
                  combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

        land_use = get_model('ecalc', 'Land_Use').objects.get(name='Grassland')
        soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
        biomass = get_model('ecalc', 'Biomass_Land_Use').objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
        CF = get_model('ecalc', 'Combustion_Land_Use').objects.get(land_use=land_use)
        get_model('ecalc', 'LandCover')(name=land_use.name, project=project, category='G',
                  biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
                  combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

        get_model('ecalc', 'Practice')(project=project,name='Default Practices').save()


########################################################################
## User permissions model
## The purpose of this model is to link users with appropriate projects.
## This will be a table in the database that will eventually hold 3 values:
## The user foreign key, the project foreign key, and their permission level
##
##
class ProjectPermissions(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    permission = models.IntegerField()

    # owner admin user

    def clone(self, new_project):
        """ Returns a copy of itself, with new FK and new FK parent, and with all new copied children """
        clone = deepcopy(self)
        clone.id = None
        clone.project = new_project
        clone.user = new_project.owner
        clone.permission = 0
        clone.save()


class Documents(models.Model):
    project = models.ForeignKey(Project)
    parent = models.ForeignKey('self', null=True)
    text = models.CharField(max_length=50, null=True)
    upload = models.FileField(upload_to = DOCUMENTS_PATH + '%Y/%m/%d/', max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.upload and not self.text:
            self.text = self.upload.name

        if not self.upload and not self.text:
            self.text = 'New Folder'

        super(Documents, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        super(Documents, self).delete(*args, **kwargs)


class ProjectBoundary(models.Model):
    project = models.ForeignKey(Project)  # there can be many boundaries to one project, ergo ManyToOne relationship
    name = models.CharField(max_length=50, null=True)
    #vertices_mapped = models.TextField(null=True, blank=True)
    poly_mapped = models.PolygonField(geography=True, null=True, blank=True)
    #vertices_reported = models.TextField(null=True, blank=True)
    poly_reported = models.PolygonField(geography=True, null=True, blank=True)

    ## Save hte center point
    center_point = models.PointField(geography=True, null=True, blank=True)
    area_reported = models.FloatField(null=True, blank=True)
    # TODO: add area functions here instead of in ASP?
    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        if self.poly_reported and not self.area_reported:
            self.poly_reported.transform(3410)
            self.area_reported = self.poly_reported.area / 10000

        super(ProjectBoundary, self).save(*args, **kwargs)

    @property
    def area_mapped(self):
        self.poly_mapped.transform(3410)
        return self.poly_mapped.area / 10000

    @property
    def vertices_mapped(self):
        if not self.poly_mapped:
            return None
        # take poly object, returns first polygon coordinates as unicode string
        return polygon_to_unicode_vertices_string(self.poly_mapped)

    @vertices_mapped.setter
    def vertices_mapped(self, vertices_string):
        if not vertices_string:
            self.poly_mapped = None
            return
        poly = from_string_vertices_to_gis_polygon(vertices_string)
        self.poly_mapped = poly

    @property
    def vertices_reported(self):
        if not self.poly_reported:
            return None
        # take poly object, returns first polygon coordinates as unicode string
        return polygon_to_unicode_vertices_string(self.poly_reported)

    @vertices_reported.setter
    def vertices_reported(self, vertices_string):
        if not vertices_string:
            self.poly_reported = None
            return
        poly = from_string_vertices_to_gis_polygon(vertices_string)
        self.poly_reported = poly


    def clone(self, new_project):
        """ Returns a copy of itself, with a new ID and new FK parent, and with all new copied children """
        clone = deepcopy(self)
        clone.id = None
        clone.project = new_project
        clone.save()  # This will create the clone and give it a new ID
        return clone


class ParcelCarbonStocksStruct():
    _fields = ['mean_agb_tc_ha',
               'mean_bgb_tc_ha',
               'mean_soc_tc_ha',
               'mean_litter_tc_ha',
               'mean_deadwood_tc_ha',
               'mean_total_tc_ha',
               'std_agb_tc_ha',
               'std_bgb_tc_ha',
               'std_soc_tc_ha',
               'std_litter_tc_ha',
               'std_deadwood_tc_ha',
               'std_total_tc_ha',
               'min_95_agb_tc_ha',
               'min_95_bgb_tc_ha',
               'min_95_soc_tc_ha',
               'min_95_litter_tc_ha',
               'min_95_deadwood_tc_ha',
               'min_95_total_tc_ha',
               'max_95_agb_tc_ha',
               'max_95_bgb_tc_ha',
               'max_95_soc_tc_ha',
               'max_95_litter_tc_ha',
               'max_95_deadwood_tc_ha',
               'max_95_total_tc_ha',
               'perc_95_agb_tc_ha',
               'perc_95_bgb_tc_ha',
               'perc_95_soc_tc_ha',
               'perc_95_litter_tc_ha',
               'perc_95_deadwood_tc_ha',
               'perc_95_total_tc_ha',
               'mean_trees_ha',
               'mean_agb_tdm_ha',
               'mean_bgb_tdm_ha',
               'std_trees_ha',
               'std_agb_tdm_ha',
               'std_bgb_tdm_ha',
               'plot_count',  # this may differ from n_plots -- includes plots with no sampling data
               'n_plots_agb',
               'n_plots_bgb',
               'n_plots_soc',
               'n_plots_litter',
               'n_plots_deadwood',
               'n_plots',  # this may differ from plot_count -- does NOT include plots with no sampling data
               'agb_tc',
               'bgb_tc',
               'soc_tc',
               'litter_tc',
               'deadwood_tc',
               'total_tc',
               'area_used',
               ]

    def __init__(self):
        for fld in self._fields:
            setattr(self, fld, 0.0)


def calculateParcelStatistics(biomass_list_data):
    '''
        This function will be used to calculate the statistics for the
        variance forms of biomass for parcels. It calculates the mean
        standard deviation, variance, t-statistic, and control chart
    '''

    if len(biomass_list_data) < 1:
        return (0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0)

    mean        = 0.0
    variance    = 0.0
    std         = 0.0
    t_statistic = 0.0
    n_plots     = 0
    min_95      = 0.0
    max_95      = 0.0
    perc_95     = 0.0

    mean     = numpy.mean(biomass_list_data)
    variance = numpy.var(biomass_list_data, ddof=1, dtype=float)

    if numpy.isnan(variance):
        variance = 0.0

    std            = numpy.sqrt(variance)
    n_plots        = len(biomass_list_data)
    standard_error = t_statistic = std / numpy.sqrt(n_plots)
    t_statistic    = scipy.stats.t.isf(0.025, n_plots - 1)

    if numpy.isnan(t_statistic):
        t_statistic = 0.0

    min_95  = mean - t_statistic * standard_error
    max_95  = mean + t_statistic * standard_error
    perc_95 = (max_95 / mean - 1) * 100

    return (mean, variance, std, n_plots, min_95, max_95, perc_95)


class Parcel(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=50, null=True)
    post_resource_identifier = models.CharField(max_length=5, default="")  # this is a unique identifier that is POST'd from client so that I can map Plot relationships after a batch PATCH which creates new resources
    #vertices_mapped = models.TextField(null=True)
    poly_mapped = models.PolygonField(geography=True, null=True, blank=True)
    #vertices_reported = models.TextField(null=True)
    poly_reported = models.PolygonField(geography=True, null=True, blank=True)

    center_point = models.PointField(geography=True, null=True, blank=True)
    area_reported = models.FloatField(null=True, blank=True)
    #aeq = models.ForeignKey('Allometric_Equation', null=True)  # this can be null, in which case the get_aeq() method returns a default
    aeq = models.ForeignKey('allometric.Equation',null=True)
    # Tier One values
    t1_agb = models.FloatField(null=True, blank=True)
    t1_bgb = models.FloatField(null=True, blank=True)
    t1_soc = models.FloatField(null=True, blank=True)
    t1_deadwood = models.FloatField(null=True, blank=True)
    t1_litter = models.FloatField(null=True, blank=True)

    # Tier Two values
    t2_agb = models.FloatField(null=True, blank=True)
    t2_bgb = models.FloatField(null=True, blank=True)
    t2_soc = models.FloatField(null=True, blank=True)
    t2_deadwood = models.FloatField(null=True, blank=True)
    t2_litter = models.FloatField(null=True, blank=True)

    mean_agb_tc_ha    = models.FloatField(default=0.0)
    std_agb_tc_ha     = models.FloatField(default=0.0)
    min_95_agb_tc_ha  = models.FloatField(default=0.0)
    max_95_agb_tc_ha  = models.FloatField(default=0.0)
    perc_95_agb_tc_ha = models.FloatField(default=0.0)
    n_plots_agb       = models.IntegerField(default=0)

    # Below Ground Biomass values
    mean_bgb_tc_ha    = models.FloatField(default=0.0)
    std_bgb_tc_ha     = models.FloatField(default=0.0)
    min_95_bgb_tc_ha  = models.FloatField(default=0.0)
    max_95_bgb_tc_ha  = models.FloatField(default=0.0)
    perc_95_bgb_tc_ha = models.FloatField(default=0.0)
    n_plots_bgb       = models.IntegerField(default=0)

    # Soil Biomass values
    mean_soc_tc_ha    = models.FloatField(default=0.0)
    std_soc_tc_ha     = models.FloatField(default=0.0)
    min_95_soc_tc_ha  = models.FloatField(default=0.0)
    max_95_soc_tc_ha  = models.FloatField(default=0.0)
    perc_95_soc_tc_ha = models.FloatField(default=0.0)
    n_plots_soc       = models.IntegerField(default=0)

    # Litter biomass values
    mean_litter_tc_ha    = models.FloatField(default=0.0)
    std_litter_tc_ha     = models.FloatField(default=0.0)
    min_95_litter_tc_ha  = models.FloatField(default=0.0)
    max_95_litter_tc_ha  = models.FloatField(default=0.0)
    perc_95_litter_tc_ha = models.FloatField(default=0.0)
    n_plots_litter       = models.IntegerField(default=0)

    # Deadwood biomass values
    mean_deadwood_tc_ha    = models.FloatField(default=0.0)
    std_deadwood_tc_ha     = models.FloatField(default=0.0)
    min_95_deadwood_tc_ha  = models.FloatField(default=0.0)
    max_95_deadwood_tc_ha  = models.FloatField(default=0.0)
    perc_95_deadwood_tc_ha = models.FloatField(default=0.0)
    n_plots_deadwood       = models.IntegerField(default=0)

    mean_trees_ha   = models.FloatField(default=0.0)
    std_trees_ha    = models.FloatField(default=0.0)

    mean_agb_tdm_ha = models.FloatField(default=0.0)
    std_agb_tdm_ha  = models.FloatField(default=0.0)

    mean_bgb_tdm_ha = models.FloatField(default=0.0)
    std_bgb_tdm_ha  = models.FloatField(default=0.0)

    area_used = models.FloatField(default=0.0)

    data_valid = models.BooleanField(default=False)

    def _calculateAgbTc(self):
        return self.mean_agb_tc_ha * self.area
    agb_tc = property(_calculateAgbTc)

    def _calculateBgbTc(self):
        return self.mean_bgb_tc_ha * self.area
    bgb_tc = property(_calculateBgbTc)

    def _calculateSocTc(self):
        return self.mean_soc_tc_ha * self.area
    soc_tc = property(_calculateSocTc)

    def _calculateLitterTc(self):
        return self.mean_litter_tc_ha * self.area
    litter_tc = property(_calculateLitterTc)

    def _calculateDeadwoodTc(self):
        return self.mean_deadwood_tc_ha * self.area
    deadwood_tc = property(_calculateDeadwoodTc)

    def _calculateTotalTc(self):
        return self.agb_tc + self.bgb_tc + self.soc_tc + \
        self.litter_tc + self.deadwood_tc
    total_tc = property(_calculateTotalTc)

    def calculateTotals(self):
        """
            This function is designed to calculate the totals of all
            the numbers that were put into the database. There is
            no point in storing them if we don't always need them.

            This function will be accessed as a property.
        """
        n_plots = self.n_plots_agb + self.n_plots_deadwood + self.n_plots_bgb \
        + self.n_plots_litter + self.n_plots_soc

        mean_total = self.mean_agb_tc_ha + self.mean_bgb_tc_ha + self.mean_soc_tc_ha\
        + self.mean_litter_tc_ha + self.mean_deadwood_tc_ha

        std_total = self.std_agb_tc_ha + self.std_bgb_tc_ha + self.std_litter_tc_ha\
        + self.std_soc_tc_ha + self.std_deadwood_tc_ha

        standard_error = std_total / numpy.sqrt(n_plots)

        if numpy.isnan(standard_error):
            standard_error = 0

        t = scipy.stats.t.isf(0.025, n_plots - 1)

        if numpy.isnan(t):
            t = 0

        min_95_total = mean_total - ( t * standard_error )
        max_95_total = mean_total + ( t * standard_error )
        perc_95_total = ( max_95_total / mean_total - 1) * 100 if mean_total else 0.0

        return (mean_total, std_total, n_plots, min_95_total, max_95_total, perc_95_total)

    tc_ha_totals = property(calculateTotals)


    def save(self, *args, **kwargs):

        if not self.area_reported and self.poly_reported:
            #self.area_reported = self.poly_reported.area
            self.area_reported= self.area_mapped

        super(Parcel, self).save(*args, **kwargs)

    def get_aeq(self):
        return self.aeq or self.project.get_aeq()

    # Allow these objects to be "hidden" from normal Django routines
    hidden = models.BooleanField(null=False, editable=False, default=False)
    objects = HiddenManager()

    @property
    def area_mapped(self):
        if self.poly_mapped:
            self.poly_mapped.transform(3410)
            return self.poly_mapped.area / 10000
        return 0.0

    @property
    def vertices_mapped(self):
        if not self.poly_mapped:
            return None
        # take poly object, returns first polygon coordinates as unicode string
        return polygon_to_unicode_vertices_string(self.poly_mapped)

    @vertices_mapped.setter
    def vertices_mapped(self, vertices_string):
        if not vertices_string:
            self.poly_mapped = None
            return
        poly = from_string_vertices_to_gis_polygon(vertices_string)
        self.poly_mapped = poly

    @property
    def vertices_reported(self):
        if not self.poly_reported:
            return None
        # take poly object, returns first polygon coordinates as unicode string
        return polygon_to_unicode_vertices_string(self.poly_reported)

    @vertices_reported.setter
    def vertices_reported(self, vertices_string):
        if not vertices_string:
            self.poly_reported = None
            return
        poly = from_string_vertices_to_gis_polygon(vertices_string)
        self.poly_reported = poly


    def clone(self, new_project):
        """ Returns a copy of itself, with a new ID and new FK parent, and with all new copied children """

        clone = deepcopy(self)
        clone.id = None
        clone.project = new_project

        clone.save()  # This will create the clone and give it a new ID

        self.clone_children(new_project, clone)

        return clone

    def clone_children(self, new_project, parcel):
        children = list(chain(self.plot_set.all()))
        for child in children:
            child.clone(parcel)  # Copy children to point to new FK id

        # Create a new AEQ
        if self.aeq:
            parcel.aeq = self.aeq.clone(new_project.owner)


    def _area(self):
        if self.area_reported is not None:
            return self.area_reported
        elif self.area_mapped is not None:
            return self.area_mapped
        return 0.0
    area = property(_area)

    def _get_parcel_carbon_stocks(self):
        # Create struct
        ret = ParcelCarbonStocksStruct()
        area = self.area  # access property here instead of multiple calls in func
        ret.area_used = area

        # counters
        plot_count = 0

        # these containers used for calculating statistics
        agb = list()
        bgb = list()
        soc = list()
        litter = list()
        deadwood = list()
        agb_tdm = list()
        bgb_tdm = list()
        trees = list()

        for plot in Plot.objects.filter(parcel=self).order_by('name'):
            plot_carbon_stocks = plot.carbon_stocks  # only call accessor once, as its a property function

            plot_count += 1
            if plot_carbon_stocks.agb_tc_ha:
                agb.append(float(plot_carbon_stocks.agb_tc_ha))
            if plot_carbon_stocks.bgb_tc_ha:
                bgb.append(float(plot_carbon_stocks.bgb_tc_ha))
            if plot_carbon_stocks.soc_tc_ha:
                soc.append(float(plot_carbon_stocks.soc_tc_ha))
            if plot_carbon_stocks.litter_tc_ha:
                litter.append(float(plot_carbon_stocks.litter_tc_ha))
            if plot_carbon_stocks.deadwood_tc_ha:
                deadwood.append(float(plot_carbon_stocks.deadwood_tc_ha))
            if plot_carbon_stocks.agb_tdm_ha:
                agb_tdm.append(float(plot_carbon_stocks.agb_tdm_ha))
            if plot_carbon_stocks.bgb_tdm_ha:
                bgb_tdm.append(float(plot_carbon_stocks.bgb_tdm_ha))
            if plot_carbon_stocks.trees_ha:
                trees.append(float(plot_carbon_stocks.trees_ha))

        variance_total = 0.0


        # calculate carbon pools statistics
        # we assume a normal distribution, a = .95, two-tailed
        if any(agb):

            mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(agb)

            ret.mean_agb_tc_ha    = mean
            ret.std_agb_tc_ha     = std
            ret.n_plots_agb       = n_plots
            ret.min_95_agb_tc_ha  = min_95
            ret.max_95_agb_tc_ha  = max_95
            ret.perc_95_agb_tc_ha = perc_95

            variance_total += variance


        if any(bgb):

            mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(bgb)

            ret.mean_bgb_tc_ha    = mean
            ret.std_bgb_tc_ha     = std
            ret.n_plots_bgb       = n_plots
            ret.min_95_bgb_tc_ha  = min_95
            ret.max_95_bgb_tc_ha  = max_95
            ret.perc_95_bgb_tc_ha = perc_95

            variance_total += variance


        if any(soc):
            mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(soc)

            ret.mean_soc_tc_ha    = mean
            ret.std_soc_tc_ha     = std
            ret.n_plots_soc       = n_plots
            ret.min_95_soc_tc_ha  = min_95
            ret.max_95_soc_tc_ha  = max_95
            ret.perc_95_soc_tc_ha = perc_95

            variance_total += variance

        if any(litter):
            mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(litter)

            ret.mean_litter_tc_ha    = mean
            ret.std_litter_tc_ha     = std
            ret.n_plots_litter       = n_plots
            ret.min_95_litter_tc_ha  = min_95
            ret.max_95_litter_tc_ha  = max_95
            ret.perc_95_litter_tc_ha = perc_95

            variance_total += variance

        if any(deadwood):
            mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(deadwood)

            ret.mean_deadwood_tc_ha    = mean
            ret.std_deadwood_tc_ha     = std
            ret.n_plots_deadwood       = n_plots
            ret.min_95_deadwood_tc_ha  = min_95
            ret.max_95_deadwood_tc_ha  = max_95
            ret.perc_95_deadwood_tc_ha = perc_95

            variance_total += variance


        # plot_count INCLUDES plots without sampling data. n_plots does NOT include plots without sampling data
        ret.plot_count = plot_count
        ret.n_plots    = max(ret.n_plots_agb, ret.n_plots_bgb, ret.n_plots_soc, ret.n_plots_litter, ret.n_plots_deadwood)

        # calculate misc statistics
        if any(agb_tdm):
            ret.mean_agb_tdm_ha = numpy.mean(agb_tdm)
            ret.std_agb_tdm_ha  = numpy.std(agb_tdm, ddof=1, dtype=float)
            if numpy.isnan(ret.std_agb_tdm_ha):
                ret.std_agb_tdm_ha = 0.0
        if any(bgb_tdm):
            ret.mean_bgb_tdm_ha = numpy.mean(bgb_tdm)
            ret.std_bgb_tdm_ha  = numpy.std(bgb_tdm, ddof=1, dtype=float)
            if numpy.isnan(ret.std_bgb_tdm_ha):
                ret.std_bgb_tdm_ha = 0.0
        if any(trees):
            ret.mean_trees_ha = numpy.mean(trees)
            ret.std_trees_ha  = numpy.std(trees, ddof=1, dtype=float)
            if numpy.isnan(ret.std_trees_ha):
                ret.std_trees_ha = 0.0

        ret.mean_total_tc_ha = ret.mean_agb_tc_ha + ret.mean_bgb_tc_ha + ret.mean_soc_tc_ha + \
        ret.mean_litter_tc_ha + ret.mean_deadwood_tc_ha
        ret.std_total_tc_ha  = sqrt(variance_total)
        standard_error       = ret.std_total_tc_ha / numpy.sqrt(ret.n_plots)
        t = scipy.stats.t.isf(.025, ret.n_plots - 1)

        if numpy.isnan(t):
            t = 0.0
        ret.min_95_total_tc_ha  = ret.mean_total_tc_ha - (t * standard_error)
        ret.max_95_total_tc_ha  = ret.mean_total_tc_ha + (t * standard_error)
        ret.perc_95_total_tc_ha = ((ret.max_95_total_tc_ha / ret.mean_total_tc_ha) - 1) * 100

        ret.agb_tc      = ret.mean_agb_tc_ha * area
        ret.bgb_tc      = ret.mean_bgb_tc_ha * area
        ret.soc_tc      = ret.mean_soc_tc_ha * area
        ret.litter_tc   = ret.mean_litter_tc_ha * area
        ret.deadwood_tc = ret.mean_deadwood_tc_ha * area
        ret.total_tc    = ret.mean_total_tc_ha * area

        return ret

    carbon_stocks = property(_get_parcel_carbon_stocks)
    
    # Do not allow user to delete the default parcel in a project (if somehow they access it!)
    def delete(self, *args, **kwargs):
        # Condition: # parcels > 1
        if self.id != self.project.default_parcel.id:
            return super(Parcel, self).delete(*args, **kwargs)  # Call the real delete command if this is not the default parcel
        else:
            return  # or silently suppress deletion. FIXME: should probably raise an exception to be handled by API/views

    def _generate_tier_1(self):

        if self.t1_agb is None:
            self.t1_agb = 0
        if self.t1_bgb is None:
            self.t1_bgb = 0
        if self.t1_deadwood is None:
            self.t1_deadwood = 0
        if self.t1_litter is None:
            self.t1_litter = 0
        if self.t1_soc is None:
            self.t1_soc = 0

        # Create struct
        ret = ParcelCarbonStocksStruct()
        area = self.area  # access property here instead of multiple calls in func
        ret.area_used = area

        ret.mean_agb_tc_ha = self.t1_agb
        ret.mean_bgb_tc_ha = self.t1_bgb
        ret.mean_soc_tc_ha = self.t1_soc
        ret.mean_deadwood_tc_ha = self.t1_deadwood
        ret.mean_litter_tc_ha = self.t1_litter
        ret.mean_total_tc_ha = ret.mean_agb_tc_ha + ret.mean_bgb_tc_ha + ret.mean_soc_tc_ha + ret.mean_litter_tc_ha + ret.mean_deadwood_tc_ha

        total = self.t1_agb + self.t1_bgb + self.t1_soc + self.t1_litter + self.t1_deadwood

        ret.agb_tc = self.t1_agb * area
        ret.bgb_tc = self.t1_bgb * area
        ret.soc_tc = self.t1_soc * area
        ret.litter_tc = self.t1_litter * area
        ret.deadwood_tc = self.t1_deadwood * area
        ret.total_tc = total * area
        if self.area:
            ret.mean_agb_tdm_ha = aeq.tc2tdm(self.t1_agb * area) / area
            ret.mean_bgb_tdm_ha = aeq.tc2tdm(self.t1_bgb * area) / area

        return ret

    tier_one = property(_generate_tier_1)

    def _generate_tier_2(self):

        if self.t2_agb is None:
            self.t2_agb = 0
        if self.t2_bgb is None:
            self.t2_bgb = 0
        if self.t2_deadwood is None:
            self.t2_deadwood = 0
        if self.t2_litter is None:
            self.t2_litter = 0
        if self.t2_soc is None:
            self.t2_soc = 0

        # Create struct
        ret = ParcelCarbonStocksStruct()
        area = self.area  # access property here instead of multiple calls in func
        ret.area_used = area

        ret.mean_agb_tc_ha = self.t2_agb
        ret.mean_bgb_tc_ha = self.t2_bgb
        ret.mean_soc_tc_ha = self.t2_soc
        ret.mean_deadwood_tc_ha = self.t2_deadwood
        ret.mean_litter_tc_ha = self.t2_litter
        ret.mean_total_tc_ha = ret.mean_agb_tc_ha + ret.mean_bgb_tc_ha + ret.mean_soc_tc_ha + ret.mean_litter_tc_ha + ret.mean_deadwood_tc_ha

        total = self.t2_agb + self.t2_bgb + self.t2_soc + self.t2_litter + self.t2_deadwood

        ret.agb_tc = self.t2_agb * area
        ret.bgb_tc = self.t2_bgb * area
        ret.soc_tc = self.t2_soc * area
        ret.litter_tc = self.t2_litter * area
        ret.deadwood_tc = self.t2_deadwood * area
        ret.total_tc = total * area

        if self.area:
            ret.mean_agb_tdm_ha = aeq.tc2tdm(self.t2_agb * area) / area
            ret.mean_bgb_tdm_ha = aeq.tc2tdm(self.t2_bgb * area) / area

        return ret

    tier_two = property(_generate_tier_2)


class PlotCarbonStocksStruct():
    _fields = ['estimated_n_trees',
               'inventory_n_trees',
               'dbh_mean',
               'dbh_sd',
               'height_mean',
               'height_sd',
               'wsg_mean',
               'wsg_sd',
               'trees_ha',
               'agb_tc_ha',
               'bgb_tc_ha',
               'agb_tdm_ha',
               'bgb_tdm_ha',
               'soc_tc_ha',
               'litter_tc_ha',
               'deadwood_tc_ha',
               'total_tc_ha',
               'equation'
               ]

    def __init__(self):
        for fld in self._fields:
            setattr(self, fld, None)


class NestedSubPlotStruct():

    def __init__(self, aeq_function, whole_plot_area, sub_plot_area, region):
        self.height_list = list()
        self.dbh_list = list()
        self.wsg_list = list()
        self.abg_kg_dm = 0.0
        self.n_trees = 0
        self.area = 0.0
        self.sub_plot_area = 0.0
        self.whole_plot_area = 0.0
        if sub_plot_area is not None:
            self.sub_plot_area = sub_plot_area  # convert from m^2 to ha
        if whole_plot_area is not None:
            self.whole_plot_area = whole_plot_area
        self.aeq_function = aeq_function
        self.region = region

    def add_tree(self, tree, ret):
        eqs = []
        self.n_trees += 1
        if tree.total_height is not None:
            self.height_list.append(tree.total_height)
        if tree.dbh is not None:
            self.dbh_list.append(tree.dbh)
        if tree.wood_gravity is not None:
            self.wsg_list.append(tree.wood_gravity)

        if self.region is None:
            self.abg_kg_dm += self.aeq_function(tree)
        else:
            species = tree.species
            genus = tree.genus
            equationspecies = None
            equations = None
            if genus:
                try:
                    equationspecies = EquationSpecies.objects.get(genus__iexact=genus, name__iexact=species)
                except:
                    try:
                        equationspecies = EquationSpecies.objects.get(genus__iexact=genus, name='')
                    except:
                        equationspecies = None
            try:
                equations = allometric.models.Equation.objects.filter(species=equationspecies, region=self.region)
                if not equations:
                    equations = allometric.models.Equation.objects.filter(species=None, region=self.region)

                if not equations:
                    raise Exception('No equation available')
            except:
                self.abg_kg_dm += self.aeq_function(tree)
                return eqs

            for equation in equations:
                temp = equation._calculate_agb(tree)
                if equation.volumetric:
                    if tree.wood_gravity:
                        temp = temp * tree.wood_gravity
                    else:
                        temp = temp * 0.7 * 1000
                elif equation.less_than_ten:
                    if not equation.is_less_than_dbh(tree.dbh):
                        temp = 0
                elif not equation.less_than_ten:
                    if equation.is_less_than_dbh(tree.dbh):
                        temp = 0
                if temp != 0:
                    eqs.append({"name":equation.name, "equation":equation.string})
                self.abg_kg_dm += temp
            return eqs

    def _sub_plot_value_extrapolated_for_whole_plot(self, value):
        try:
            return value * self.whole_plot_area / self.sub_plot_area
        except ZeroDivisionError:
            return 0.0

    def get_weighted_tree_count(self):
        return self._sub_plot_value_extrapolated_for_whole_plot(self.n_trees)

    def get_weighted_abg_kg_dm(self):
        return self._sub_plot_value_extrapolated_for_whole_plot(self.abg_kg_dm)

    def get_dbh_weighted_sum(self):
        return self._sub_plot_value_extrapolated_for_whole_plot(sum(self.dbh_list))

    def get_dbh_weighted_sum_of_squared_differences(self, sample_mean):
        return self._sub_plot_value_extrapolated_for_whole_plot(sum(map(lambda x: (x - sample_mean)**2, self.dbh_list))) if sample_mean else 0.0  # prevent possibility of ZeroDivisionError

    def get_wsg_weighted_sum(self):
        return self._sub_plot_value_extrapolated_for_whole_plot(sum(self.wsg_list))

    def get_wsg_weighted_sum_of_squared_differences(self, sample_mean):
        return self._sub_plot_value_extrapolated_for_whole_plot(sum(map(lambda x: (x - sample_mean)**2, self.wsg_list))) if sample_mean else 0.0  # prevent possibility of ZeroDivisionError

    def get_height_weighted_sum(self):
        return self._sub_plot_value_extrapolated_for_whole_plot(sum(self.height_list))

    def get_height_weighted_sum_of_squared_differences(self, sample_mean):
        return self._sub_plot_value_extrapolated_for_whole_plot(sum(map(lambda x: (x - sample_mean)**2, self.height_list))) if sample_mean else 0.0  # prevent possibility of ZeroDivisionError




class Plot(models.Model):
    UNKNOWN = 'polygon'
    SQUARE = 'polygon'
    CIRCLE = 'circular'
    RECTANGLE = 'rectangular'
    POLYGON = 'polygon'
    SHAPES = [(UNKNOWN, 'unknown'),
              (SQUARE, 'square'),
              (CIRCLE, 'circular'),
              (RECTANGLE, 'rectangular'),
              (POLYGON, 'polygon')
              ]

    # META INFORMATION
    parcel = models.ForeignKey(Parcel, null=True, blank=True, default=None)
    project = models.ForeignKey(Project, null=True)
    name = models.CharField(max_length=50, null=True)
    #allometric_equation = models.CharField(max_length=30, null=True)  # TODO: Make ForeignKey to allometric_Eq object
    root_shoot_ratio = models.FloatField(null=True, blank=True)
    #aeq = models.ForeignKey('Allometric_Equation', null=True)  # this can be null, in which case the get_aeq() method returns a default
    objects = models.GeoManager()
    region = models.ForeignKey('allometric.EquationRegion', null=True)
    aeq = models.ForeignKey('allometric.Equation',null=True)
    calculate_by_species = models.BooleanField(default=False)

    def get_aeq(self):
        return self.aeq or self.parcel.get_aeq()

    def _allometric_equation(self):
        return self.get_aeq().name
    allometric_equation = property(_allometric_equation)

    # DESCRIPTIVE META INFORMATION
    sample_date = models.CharField(max_length=30, null=True)
    sample_start_time = models.CharField(max_length=30, null=True)
    sample_end_time = models.CharField(max_length=30, null=True)
    sample_crew = models.CharField(max_length=80, null=True)
    description = models.CharField(max_length=100, null=True)
    gps_latitude = models.CharField(max_length=30, null=True)
    gps_longitude = models.CharField(max_length=30, null=True)
    elevation = models.CharField(max_length=30, null=True)
    slope_condition = models.CharField(max_length=30, null=True)
    hemi_photo_center = models.CharField(max_length=30, null=True)
    hemi_photo_north = models.CharField(max_length=30, null=True)
    hemi_photo_east = models.CharField(max_length=30, null=True)
    hemi_photo_south = models.CharField(max_length=30, null=True)
    hemi_photo_west = models.CharField(max_length=30, null=True)
    horiz_photo_north = models.CharField(max_length=30, null=True)
    horiz_photo_east = models.CharField(max_length=30, null=True)
    horiz_photo_south = models.CharField(max_length=30, null=True)
    horiz_photo_west = models.CharField(max_length=30, null=True)
    weather = models.CharField(max_length=100, null=True)
    comments = models.CharField(max_length=200, null=True)

    # SOIL INFORMATION
    soil_serial_number = models.CharField(max_length=30, null=True)
    soil_date = models.CharField(max_length=30, null=True)
    soil_start_time = models.CharField(max_length=30, null=True)
    soil_end_time = models.CharField(max_length=30, null=True)
    soil_crew = models.CharField(max_length=200, null=True)
    soil_carbon_concentration = models.FloatField(null=True, blank=True)
    soil_depth = models.FloatField(null=True, blank=True)
    soil_mass_air_sample = models.FloatField(null=True, blank=True)
    soil_mass_air_sample_coarse_fragments = models.FloatField(null=True, blank=True)
    soil_mass_air_subsample_plus_tin = models.FloatField(null=True, blank=True)
    soil_mass_oven_subsample = models.FloatField(null=True, blank=True)
    soil_mass_tin = models.FloatField(null=True, blank=True)
    soil_gravimetric_moisture_content = models.FloatField(null=True, blank=True)
    soil_mass_oven_sample = models.FloatField(null=True, blank=True)
    soil_volume = models.FloatField(null=True, blank=True)
    soil_bulk_density = models.FloatField(null=True, blank=True)
    soil_coarse_fragments_ratio = models.FloatField(null=True, blank=True)

    # NESTED PLOTS & BOUNDS
    subplot_1_name = models.CharField(max_length=30, null=True)
    subplot_1_area_m2 = models.FloatField(null=True, blank=True)
    subplot_1_lower_bound = models.FloatField(null=True, blank=True)
    subplot_1_upper_bound = models.FloatField(null=True, blank=True)
    subplot_2_name = models.CharField(max_length=30, null=True)
    subplot_2_area_m2 = models.FloatField(null=True, blank=True)
    subplot_2_lower_bound = models.FloatField(null=True, blank=True)
    subplot_2_upper_bound = models.FloatField(null=True, blank=True)
    subplot_3_name = models.CharField(max_length=30, null=True)
    subplot_3_area_m2 = models.FloatField(null=True, blank=True)
    subplot_3_lower_bound = models.FloatField(null=True, blank=True)
    subplot_3_upper_bound = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.root_shoot_ratio:
            self.root_shoot_ratio = 0.0

        if self.dimensions_reported and not self.area_reported:
            if self.shape_reported == 'circular' or self.shape_reported == 'circle':
                self.area_reported = float(self.dimensions_reported)
            else:
                dimensions = self.dimensions_reported.split('x')
                area = float(dimensions[0]) * float(dimensions[1])
                self.area_reported = area

        if self.parcel and not self.project:
            self.project = self.parcel.project




        super(Plot, self).save(*args, **kwargs)

    def _get_subplot_1_area(self):
        if self.subplot_1_area_m2 is None:
            return 0.0
        return self.subplot_1_area_m2 / 10000.0

    def _get_subplot_2_area(self):
        if self.subplot_2_area_m2 is None:
            return 0.0
        return self.subplot_2_area_m2 / 10000.0

    def _get_subplot_3_area(self):
        if self.subplot_3_area_m2 is None:
            return 0.0
        return self.subplot_3_area_m2 / 10000.0

    subplot_1_area = property(_get_subplot_1_area)
    subplot_2_area = property(_get_subplot_2_area)
    subplot_3_area = property(_get_subplot_3_area)

    # MAPPED SHAPE
    shape_mapped = models.CharField(max_length=15, choices=SHAPES, default=UNKNOWN, null=True)
    dimensions_mapped = models.CharField(max_length=30, null=True)
    #vertices_mapped = models.TextField(null=True, blank=True)  # do we validate to 4 coords ? can we change to CharField for performance boost?
    poly_mapped = models.PolygonField(geography=True, null=True, blank=True)

    center_point = models.PointField(geography=True, null=True, blank=True)

    # REPORTED SHAPE
    shape_reported = models.CharField(max_length=15, choices=SHAPES, default=UNKNOWN, null=True)
    dimensions_reported = models.CharField(max_length=30, null=True)
    #vertices_reported = models.TextField(null=True, blank=True)
    poly_reported = models.PolygonField(geography=True, null=True, blank=True)
    area_reported = models.FloatField(null=True, blank=True)

    # UTM VERTICES [not sure if legacy or existing use]
    utm_vertices_mapped = models.TextField(null=True, blank=True)
    utm_vertices_reported = models.TextField(null=True, blank=True)

    # ADDITIONAL CARBON POOLS
    litter_tc_ha = models.FloatField(default=0.0)
    deadwood_tc_ha = models.FloatField(default=0.0)
    nontree_agb_tc_ha = models.FloatField(default=0.0)
    nontree_bgb_tc_ha = models.FloatField(default=0.0)

    ## Carbon stocks
    estimated_n_trees = models.FloatField(null=True)
    trees_ha       = models.FloatField(null=True)

    dbh_mean       = models.FloatField(null=True)
    wsg_mean       = models.FloatField(null=True)
    height_mean    = models.FloatField(null=True)

    dbh_sd         = models.FloatField(null=True)
    wsg_sd         = models.FloatField(null=True)
    height_sd      = models.FloatField(null=True)

    agb_tdm_ha     = models.FloatField(null=True, default=0.0)
    agb_tc_ha      = models.FloatField(null=True, default=0.0)

    bgb_tdm_ha     = models.FloatField(null=True, default=0.0)
    bgb_tc_ha      = models.FloatField(null=True, default=0.0)

    litter_tc_ha   = models.FloatField(null=True, default=0.0)
    deadwood_tc_ha = models.FloatField(null=True, default=0.0)

    data_valid = models.BooleanField(default=False)

    @property
    def total_tc_ha(self):
        """
            Function that calculates the tC/ha that will be a property. Decided not to
            store the total as that value could change repeatedly.
        """
        l = [self.agb_tc_ha, self.bgb_tc_ha, self.soc_tc_ha,
        self.litter_tc_ha, self.deadwood_tc_ha]

        total = 0.0
        for i in l:
            total += i if i else 0.0

        return total

    def calculateSOC(self):
        """
            Function that calculates the tC/ha for soil carbon. This function exists
            because calculating soil requires a lot of other information.
        """
        if all(self.soil_depth, self.soil_carbon_concentration, self.soil_bulk_density,\
            self.soil_coarse_fragments_ratio):
            return (self.soil_carbon_concentration * self.soil_bulk_density *\
             self.soil_depth * ( 1 - self.soil_coarse_fragments_ratio))*100
        return 0.0

    @property
    def area_mapped(self):
        if self.dimensions_mapped:
            if 'x' in self.dimensions_mapped:
                v = self.dimensions_mapped.split('x')
                return float(v[0]) * float(v[0]) / 10000
            else:
                return float(self.dimensions_mapped)**2 * 3.14 / 10000
        return 0.0

    def _area(self):
        if self.area_reported is not None and self.area_reported != 0.0:
            return self.area_reported / 10000
        elif self.area_mapped is not None and self.area_mapped != 0.0:
            return self.area_mapped / 10000
        return 0.0

    area = property(_area)

    @property
    def vertices_mapped(self):
        if not self.poly_mapped:
            return None
        # take poly object, returns first polygon coordinates as unicode string
        return polygon_to_unicode_vertices_string(self.poly_mapped)

    @vertices_mapped.setter
    def vertices_mapped(self, vertices_string):
        if not vertices_string:
            self.poly_mapped = None
            return
        poly = from_string_vertices_to_gis_polygon(vertices_string)
        self.poly_mapped = poly

    @property
    def vertices_reported(self):
        if not self.poly_reported:
            return None
        # take poly object, returns first polygon coordinates as unicode string
        return polygon_to_unicode_vertices_string(self.poly_reported)

    @vertices_reported.setter
    def vertices_reported(self, vertices_string):
        if not vertices_string:
            self.poly_reported = None
            return
        poly = from_string_vertices_to_gis_polygon(vertices_string)
        self.poly_reported = poly

    # IS ___ ENABLED?
    def _has_soil_data(self):
        return bool(self.soc_tc_ha)
    has_soil_data = property(_has_soil_data)

    def _has_biomass_data(self):
        return Tree.objects.filter(plot=self).count() != 0  # FIXME: I could move this into the _get_carbon_stocks() func as it is frequently accessed at the same time, to improve performance?
    has_biomass_data = property(_has_biomass_data)

    def _has_deadwood_data(self):
        return bool(self.deadwood_tc_ha)
    has_deadwood_data = property(_has_deadwood_data)

    def _has_litter_data(self):
        return bool(self.litter_tc_ha)
    has_litter_data = property(_has_litter_data)

    def clone(self, new_parcel):
        """ Returns a copy of itself, with a new ID and new FK parent, and with all new copied children """
        clone = deepcopy(self)
        clone.id = None
        clone.parcel = new_parcel
        clone.save()  # This will create the clone and give it a new ID
        children = list(chain(self.tree_set.all()))
        for child in children:
            child.clone(clone)  # Copy children to point to new FK id

        # Create a new AEQ
        if self.aeq:
            clone.aeq = self.aeq.clone(new_parcel.project.owner)

        return clone

    def _get_plot_carbon_stocks(self):
        # In lieu of singular propeties, I return a tuple as many of these are calculated
        # after aggregating the tree set ... this improves performance as I only need to
        # iterate over the tree_set once.

        # Create struct
        ret = PlotCarbonStocksStruct()
        ret.equation = []
        eqs = []
        if self.has_biomass_data:
            # Identify allometric eq to use
            if self.get_aeq():
                aeq_function = self.get_aeq()._calculate_agb

            # Create some tree_set containers
            inventory_n_trees = 0
            whole_plot = NestedSubPlotStruct(aeq_function, self.area, self.area, self.region)
            sub_plot_1 = NestedSubPlotStruct(aeq_function, self.area, self.subplot_1_area, self.region)
            sub_plot_2 = NestedSubPlotStruct(aeq_function, self.area, self.subplot_2_area, self.region)
            sub_plot_3 = NestedSubPlotStruct(aeq_function, self.area, self.subplot_3_area, self.region)
            all_subplots = list([whole_plot, sub_plot_1, sub_plot_2, sub_plot_3])

            # Sort trees into whole- or sub- plots
            for tree in Tree.objects.filter(plot=self):
                inventory_n_trees += 1
                if tree.dbh is None:
                    continue
                elif tree.dbh > self.subplot_1_lower_bound and tree.dbh <= self.subplot_1_upper_bound:
                    eqs = sub_plot_1.add_tree(tree, ret.equation)
                elif tree.dbh > self.subplot_2_lower_bound and tree.dbh <= self.subplot_2_upper_bound:
                    eqs = sub_plot_2.add_tree(tree, ret.equation)
                elif tree.dbh > self.subplot_3_lower_bound and tree.dbh <= self.subplot_3_upper_bound:
                    eqs = sub_plot_3.add_tree(tree, ret.equation)
                else:  # whole plot
                    eqs = whole_plot.add_tree(tree, ret.equation)

                if eqs:
                    for e in eqs:
                        if e not in ret.equation:
                            ret.equation.append(e);

            # Save the count
            ret.inventory_n_trees = inventory_n_trees
            ret.estimated_n_trees = sum(map(lambda x: x.get_weighted_tree_count(), all_subplots))
            if self.area is not None and self.area != 0.0:
                ret.trees_ha = ret.estimated_n_trees / self.area
            else:
                ret.trees_ha = None
            #ret.trees_ha = ret.estimated_n_trees / self.area if self.area is not None else None  # prevent possibility of ZeroDivisionError

            # Calculate mean
            sum_of_height = sum(map(lambda x: x.get_height_weighted_sum(), all_subplots))
            sum_of_dbh = sum(map(lambda x: x.get_dbh_weighted_sum(), all_subplots))
            sum_of_wsg = sum(map(lambda x: x.get_wsg_weighted_sum(), all_subplots))
            ret.height_mean = sum_of_height / ret.estimated_n_trees if ret.estimated_n_trees is not None and ret.estimated_n_trees != 0.0 else None  # prevent possibility of ZeroDivisionError
            ret.dbh_mean = sum_of_dbh / ret.estimated_n_trees if ret.estimated_n_trees is not None and ret.estimated_n_trees != 0.0 else None  # prevent possibility of ZeroDivisionError
            ret.wsg_mean = sum_of_wsg / ret.estimated_n_trees if ret.estimated_n_trees is not None and ret.estimated_n_trees != 0.0 else None  # prevent possibility of ZeroDivisionError

            # Calculate st dv
            dbh_sum_of_squared_differences = sum(map(lambda x: x.get_dbh_weighted_sum_of_squared_differences(ret.dbh_mean), all_subplots))
            wsg_sum_of_squared_differences = sum(map(lambda x: x.get_wsg_weighted_sum_of_squared_differences(ret.wsg_mean), all_subplots))
            height_sum_of_squared_differences = sum(map(lambda x: x.get_height_weighted_sum_of_squared_differences(ret.height_mean), all_subplots))
            ret.height_sd = sqrt(height_sum_of_squared_differences/(ret.estimated_n_trees - 1)) if ret.estimated_n_trees is not None and ret.estimated_n_trees > 1 else None  # prevent possibility of ZeroDivisionError
            ret.dbh_sd = sqrt(dbh_sum_of_squared_differences/(ret.estimated_n_trees - 1)) if ret.estimated_n_trees is not None and ret.estimated_n_trees > 1 else None  # prevent possibility of ZeroDivisionError
            ret.wsg_sd = sqrt(wsg_sum_of_squared_differences/(ret.estimated_n_trees - 1)) if ret.estimated_n_trees is not None and ret.estimated_n_trees > 1 else None  # prevent possibility of ZeroDivisionError

            # Calculate AGB carbon stocks in tDM and tC
            sum_abg_kg_dm = sum(map(lambda x: x.get_weighted_abg_kg_dm(), all_subplots))

            ret.agb_tdm_ha = aeq.kdm2tdm(sum_abg_kg_dm) / self.area if self.area is not None and self.area != 0.0 else None  # prevent possibility of ZeroDivisionError
            ret.agb_tc_ha = aeq.kdm2tc(sum_abg_kg_dm) / self.area if self.area is not None and self.area != 0.0 else None  # prevent possibility of ZeroDivisionError

            ret.bgb_tdm_ha = aeq.agb2bgb(ret.agb_tdm_ha, self.root_shoot_ratio) if ret.agb_tdm_ha is not None else None  # prevent possibility of TypeError
            ret.bgb_tc_ha = aeq.agb2bgb(ret.agb_tc_ha, self.root_shoot_ratio) if ret.agb_tdm_ha is not None else None  # prevent possibility of TypeError

            if self.nontree_agb_tc_ha is not None:
                ret.agb_tc_ha += self.nontree_agb_tc_ha
                ret.agb_tdm_ha += aeq.tc2tdm(self.nontree_agb_tc_ha)
            if self.nontree_bgb_tc_ha is not None:
                ret.bgb_tc_ha += self.nontree_bgb_tc_ha
                ret.bgb_tdm_ha += aeq.tc2tdm(self.nontree_bgb_tc_ha)

        else:  # case- no trees are uploaded
            ret.inventory_n_trees = None  # FIXME: these definitions can be removed since they are init'd as nulls anyway
            ret.estimated_n_trees = None  # THESE SHOULD NEVER BE NONE!!!
            ret.trees_ha = None
            ret.height_mean = None
            ret.dbh_mean = None
            ret.wsg_mean = None
            ret.height_sd = None
            ret.dbh_sd = None
            ret.wsg_sd = None
            ret.agb_tdm_ha = None
            ret.agb_tc_ha = None
            ret.bgb_tdm_ha = None
            ret.bgb_tc_ha = None
            # its possible they specified a non-tree biomass pool ...
            if self.nontree_agb_tc_ha is not None:
                ret.agb_tc_ha = self.nontree_agb_tc_ha
                ret.agb_tdm_ha = aeq.tc2tdm(self.nontree_agb_tc_ha)
            if self.nontree_bgb_tc_ha is not None:
                ret.bgb_tc_ha = self.nontree_bgb_tc_ha
                ret.bgb_tdm_ha = aeq.tc2tdm(self.nontree_bgb_tc_ha)

        # placeholders
        ret.soc_tc_ha = self.soc_tc_ha
        ret.litter_tc_ha = self.litter_tc_ha
        ret.deadwood_tc_ha = self.deadwood_tc_ha

        # total
        ret.total_tc_ha = 0.0
        ret.total_tc_ha += float(ret.agb_tc_ha or 0.0)  # this value may be null if there is no data
        ret.total_tc_ha += float(ret.bgb_tc_ha or 0.0)
        ret.total_tc_ha += float(ret.soc_tc_ha or 0.0)
        ret.total_tc_ha += float(ret.litter_tc_ha or 0.0)
        ret.total_tc_ha += float(ret.deadwood_tc_ha or 0.0)
        if (not self.has_biomass_data) and (not self.has_deadwood_data) and (not self.has_soil_data) and (not self.has_litter_data):
            ret.total_tc_ha = None
        return ret

    carbon_stocks = property(_get_plot_carbon_stocks)

    def _get_soc_tc_ha(self):
        if (self.soil_depth is not None) and \
           (self.soil_carbon_concentration is not None) and \
           (self.soil_bulk_density is not None) and \
           (self.soil_coarse_fragments_ratio is not None):
            # Return the computed SOC
            soc_tc_ha = (self.soil_carbon_concentration * self.soil_bulk_density * self.soil_depth * (1 - self.soil_coarse_fragments_ratio))*100
            return soc_tc_ha
        else:
            # Return null for no data
            return None
    soc_tc_ha = property(_get_soc_tc_ha)

    def _update_tree_aeq_association(self):
        '''
            The purpose of this function is to reset the allometric equations to be
            used for the individual trees.
        '''
        if self.region:
            for i in self.tree_set.all():
                genus           = i.genus
                species         = i.species
                dbh             = i.dbh
                wood_gravity    = i.wood_gravity
                equationSpecies = None
                equations       = None

                i.aeqs.clear()

                try:
                    equationSpecies = get_model('allometric','EquationSpecies').objects.get(genus=genus, name=species)
                except:
                    try:
                        if not equationSpecies:
                            equationSpecies = get_model('allometric','EquationSpecies').objects.get(genus=genus, name='species')
                    except:
                        equationSpecies = None

                equations = get_model('allometric','Equation').objects.filter(region=self.region, species=equationSpecies)
                if not equations:
                    equations = get_model('allometric','Equation').objects.filter(region=self.region, species=None)

                for z in equations:
                    i.aeqs.add(z)

                i.save()



class Tree(models.Model):
    plot = models.ForeignKey(Plot)
    genus = models.CharField(max_length=60, null=True, blank=True)
    species = models.CharField(max_length=60, null=True, blank=True)
    dbh = models.FloatField(null=True, blank=True)
    total_height = models.FloatField(null=True, blank=True)
    crown_d_max = models.FloatField(null=True, blank=True)
    crown_d_90 = models.FloatField(null=True, blank=True)
    multistem = models.CharField(max_length=10, null=True, blank=True)  # TODO: replace with models.NullBooleanField()
    wood_gravity = models.FloatField(null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)
    excel_row = models.IntegerField(null=True, blank=True)
    used_in_calculations = models.BooleanField(default=True)
    aeqs = models.ManyToManyField('allometric.Equation')

    def clone(self, new_plot):
        """ Returns a copy of itself, with a new ID and new FK parent """
        clone = deepcopy(self)
        clone.id = None
        clone.plot = new_plot
        clone.save()  # This will create the clone and give it a new ID
        return clone

    class Meta:
        ordering = ['excel_row']

@receiver(post_save, sender=Tree)
def treePostSaveSignal(sender, **kwargs):
    if kwargs['created']:
        if kwargs['instance'].plot.calculate_by_species:
            kwargs['instance'].plot._update_tree_aeq_association()

