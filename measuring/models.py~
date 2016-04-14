"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
For future programmmers, the third file to read to understand the mrv are the models.py files inside the sub project folders within the mrv. Each class in this
models files represent a table in the database. The most common used classes or tables are Plot, Parcel, Project, Tree, Project Boundary, Equation.  When a user upload 
excel with plot, parcel, and project informatiom the appropriate model create a row in the parcel, plolt, and project tables. Similarily, when a user create a point or polygon or upload a shape file that represents a parcel, plot, or polygon, the appropriate model create a row in the database for the appropriate table. Each class contains 
properties. If you want to use the properties of a model in your view or template, use django queries that returns model instead of raw data from the tables.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""




import scipy
import numpy
from django.db import models
from mrvapi.models import Project, Parcel, Plot, Tree
from mrv_toolbox.settings import IMAGES_FOLDER_PATH

## Are we using a model for the image uploads??

class ImageModel(models.Model):
    plot = models.ForeignKey(Plot)
    name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to = 'static/images/')

class TreeAEQ(models.Model):
    tree = models.ForeignKey(Tree)
    aeq = models.ForeignKey('allometric.Equation')
    parcel = models.ForeignKey(Parcel)
    plot = models.ForeignKey(Plot, null=True)
"""
class ProjectCarbonStock(models.Model):
        Project Carbon Stock represents the total carbon found within
        a single project. It has a To-One relationship with a single
        project.

    # Defining the relationship to the project
    project         = models.OneToOneField(Project)

    # Carbon values for the project
    agb_tc          = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    bgb_tc          = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    soc_tc          = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    litter_tc       = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    deadwood_tc     = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    total_tc 		= models.DecimalField(max_digits=14, decimal_places=4, default=0.0)
    total_area_used = models.DecimalField(max_digits=14, decimal_places=4, default=0.0)

    # Determines if the data is valid or not. False, data must be
    # recalculated. True, data is valid.
    data_valid      = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.total_tc:
            self.total_tc = self.agb_tc + self.bgb_tc + self.soc_tc + self.litter_tc \
            + self.deadwood_tc
        #import pdb;  pdb.set_trace()
        super(ProjectCarbonStock, self).save(*args, **kwargs)


class ParcelCarbonStockTierThree(models.Model):
        Parcel Carbon Stock represents the total carbon found iwthin a single parcel.
        It has a to-one relationship with a singe parcel, as well as a to-one relationship
        with a project and a ProjectCarbonStock

    # Defining necessary relationships so we can retrieve the data
    # for calculations easily.
    parcel = models.OneToOneField(Parcel)
    # One to many relationship
    projectCarbonStock = models.ForeignKey(ProjectCarbonStock)

    # Carbon values for the parcel

    # Above Ground Biomass values
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
        return self.mean_agb_tc_ha * self.parcel.area
    agb_tc = property(_calculateAgbTc)

    def _calculateBgbTc(self):
        return self.mean_bgb_tc_ha * self.parcel.area
    bgb_tc = property(_calculateBgbTc)

    def _calculateSocTc(self):
        return self.mean_soc_tc_ha * self.parcel.area
    soc_tc = property(_calculateSocTc)

    def _calculateLitterTc(self):
        return self.mean_litter_tc_ha * self.parcel.area
    litter_tc = property(_calculateLitterTc)

    def _calculateDeadwoodTc(self):
        return self.mean_deadwood_tc_ha * self.parcel.area
    deadwood_tc = property(_calculateDeadwoodTc)

    # Calculate the total standard deviation
    def calculateTotals(self):
            This function is designed to calculate the totals of all
            the numbers that were put into the database. There is
            no point in storing them if we don't always need them.

            This function will be accessed as a property.
        n_plots = self.n_plots_agb + self.n_plots_deadwood + self.n_plots_bgb \
        + self.n_plots_litter + self.n_plots_soc

        mean_total = self.mean_agb_tc_ha + self.mean_bgb_tc_ha + self.mean_soc_tc_ha\
        + self.mean_litter_tc_ha + self.mean_deadwood_tc_ha

        std_total = self.std_agb_tc_ha + self.std_bgb_tc_ha + self.std_litter_tc_ha\
        + self.std_soc_tc_ha + self.std_deadwood_tc_ha

        standard_error = std_total / numpy.sqrt(n_plots)

        t = scipy.stats.t.isf(0.025, n_plots - 1)

        if numpy.isnan(t):
            t = 0

        min_95_total = mean_total - ( t * standard_error )
        max_95_total = mean_total + ( t * standard_error )
        perc_95_total = ( max_95_total / mean_total - 1) * 100

        return (mean_total, std_total, n_plots, min_95_total, max_95_total, perc_95_total)

    tc_ha_totals = property(calculateTotals)

class PlotCarbonStock(models.Model):
        Parcel Carbon Stock represents the total carbon found within a single plot.
        It has a to-one relationship with a singe parcel, as well as a to-one relationship
        with a project and a ProjectCarbonStock

    plot = models.OneToOneField(Plot)
    parcelCarbonStock = models.ForeignKey(ParcelCarbonStockTierThree, null=True)

    estimated_n_trees = models.FloatField(null=True)
    trees_ha       = models.FloatField(null=True)

    dbh_mean       = models.FloatField(null=True)
    wsg_mean       = models.FloatField(null=True)
    height_mean    = models.FloatField(null=True)

    dbh_sd         = models.FloatField(null=True)
    wsg_sd         = models.FloatField(null=True)
    height_sd      = models.FloatField(null=True)

    agb_tdm_ha     = models.FloatField(null=True)
    agb_tc_ha      = models.FloatField(null=True)

    bgb_tdm_ha     = models.FloatField(null=True)
    bgb_tc_ha      = models.FloatField(null=True)

    soc_tc_ha      = models.FloatField(null=True)
    litter_tc_ha   = models.FloatField(null=True)
    deadwood_tc_ha = models.FloatField(null=True)

    data_valid = models.BooleanField(default=False)

            Function that calculates the tC/ha that will be a property. Decided not to
            store the total as that value could change repeatedly.
        return self.agb_tc_ha + self.bgb_tc_ha + self.soc_tc_ha + \
        self.litter_tc_ha + self.deadwood_tc_ha

    total_tc_ha = property(calculateTotal)

    def calculateSOC(self):
            Function that calculates the tC/ha for soil carbon. This function exists
            because calculating soil requires a lot of other information.
        if all(self.plot.soil_depth, self.plot.soil_carbon_concentration, self.plot.soil_bulk_density,\
            self.plot.soil_coarse_fragments_ratio):
            return (self.plot.soil_carbon_concentration * self.plot.soil_bulk_density *\
             self.plot.soil_depth * ( 1 - self.plot.soil_coarse_fragments_ratio))*100
        return 0.0

    def calculate(self):
        trees = self.plot.trees_set
"""
