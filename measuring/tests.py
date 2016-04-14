
#This file demonstrates writing tests using the unittest module. These will pass
#when you run "manage.py test".

#Replace this with more appropriate tests for your application.

import calculations
import random
from django.test import TestCase
from mrvapi.models import Project, Parcel, Plot, Tree
from models import ParcelCarbonStockTierThree
from django.contrib.auth.models import User
from allometric.models import Equation, EquationRegion, EquationSpecies
from mrvutils.forms import BiomassXLSUploadForm
from measuring.tasks import *
from celery.result import AsyncResult
from django.test.runner import DiscoverRunner
from djcelery.contrib.test_runner import _set_eager
from django.test.client import RequestFactory

class CeleryDiscoverRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        _set_eager()
        super(CeleryDiscoverRunner, self).setup_test_environment(**kwargs)

class TestCalculations(TestCase):
    fixtures = ['allometric.json', 'mrvapi.json', 'ecalc.json']
    def setUp(self):
        self.user = User.objects.get(id=1)
        #CDR = CeleryDiscoverRunner()
        #CDR.setup_test_environment()

    def test_calculations(self):
            Test the calculations to ensure proper calculations
        #create project, parcel, plot
        project = Project.objects.create(owner=self.user, aeq=Equation.objects.get(id=7))
        p = Parcel.objects.create(project=project,area_reported=100,aeq=Equation.objects.get(id=7))
        pl = Plot.objects.create(parcel=p, project=project, root_shoot_ratio=.33, aeq=Equation.objects.get(id=7), area_reported=100)
        pl.deadwood_tc_ha = 10
        pl.litter_tc_ha = 10
        pl.nontree_agb_tc_ha = 10
        pl.nontree_bgb_tc_ha = 10
        pl.save()

        Tree.objects.create(plot=pl, dbh=10)
        Tree.objects.create(plot=pl, dbh=12)
        Tree.objects.create(plot=pl, dbh=5)
        Tree.objects.create(plot=pl, dbh=4)
        Tree.objects.create(plot=pl, dbh=15)

        result = calculateTotalCarbonStocks.delay(project.id)
        r = AsyncResult(result.id).ready()
        f = AsyncResult(result.id).failed()


        #task1 = parcelCalculate(p.id)
        print "result.backend: %s" % (result.backend)
        print "AsyncResult(result.id).ready(): %s" % (AsyncResult(result.id).ready())
        print "AsyncResult(result.id).state: %s" % (AsyncResult(result.id).state)
        print "AsyncResult(result.id).result: %s" % (AsyncResult(result.id).result)
        print "AsyncResult(result.id).failed(): %s" % (AsyncResult(result.id).failed())
        print "result.app: %s" % (result.app)
        print "result.id: %s" % (result.id)
        print "--------------------------------------"
        #spin while not ready
        while not r:
            print "AsyncResult(result.id).state: %s" % (AsyncResult(result.id).state)
        print "ready"
        #ready!
        print "--------------------------------------"
        print "AsyncResult(result.id).ready(): %s" % (AsyncResult(result.id).ready())
        print "AsyncResult(result.id).state: %s" % (AsyncResult(result.id).state)
        print "AsyncResult(result.id).result: %s" % (AsyncResult(result.id).result)
        print "AsyncResult(result.id).failed(): %s" % (AsyncResult(result.id).failed())
        print "--------------------------------------"

        proj = Project.objects.latest('pk')
        parcel = Parcel.objects.get(project=proj)
        parcel_stocks = ParcelCarbonStockTierThree.objects.get(parcel=parcel)
        print "parcel_stocks.parcel: \t %s" % (parcel_stocks.parcel)
        print "parcel.area_reported: \t %s" % (parcel.area_reported)
        print "parcel_stocks.mean_deadwood_tc_ha: \t %s" % (parcel_stocks.mean_deadwood_tc_ha)
        print "parcel_stocks.mean_agb_tc_ha: \t %s" % (parcel_stocks.mean_agb_tc_ha)
        print "--------------------------------------"

        self.assertEqual(int(parcel_stocks.agb_tc), 2212)
        self.assertEqual(int(parcel_stocks.bgb_tc), 1400)
        self.assertEqual(int(parcel_stocks.litter_tc), 1000)
        self.assertEqual(int(parcel_stocks.deadwood_tc), 1000)

        project.delete()
        return True

    def test_calculations_by_species(self):
        ## Create the few allometric equations that I need as well as the
        ## species
        region = EquationRegion.objects.get(id=4)
        species1 = EquationSpecies.objects.create(name='crenulata', genus='Terminalia')
        species2 = EquationSpecies.objects.create(name='tomentosa', genus='Terminalia')
        species3 = EquationSpecies.objects.create(name='mearnsu', genus='Acacia')

        equation1v = Equation.objects.create(name='Terminalia crenulata', string='(-0.203947 + 3.159215(dbh/100))^2',\
            owner=self.user, public=True, region=region, volumetric=True, species=species1)
        equation2v = Equation.objects.create(name='Terminalia tomentosa', string='(-0.203947 + 3.159215(dbh/100))^2',\
            owner=self.user, public=True, region=region, volumetric=True, species=species2)
        equation3v = Equation.objects.create(name='Acacia mearnsu', string='(-0.143393+3.040067(dbh/100))^2',\
            owner=self.user, public=True, region=region, volumetric=True, species=species3)

        T_crenulata_b_1 = Equation.objects.create(name='Terminalia crenulata b1', string='1815.5165(dbh/100)^3 - 1348.7147(dbh/100)^2 + 594.0835(dbh/100) - 29.0793',\
            owner=self.user, public=True, region=region, species=species1)
        T_crenulata_b_2 = Equation.objects.create(name='Terminalia crenulata b2', string='44.8486(dbh/100)^2 - 8.7590(dbh/100) + 1.2305',\
            owner=self.user, public=True, region=region, species=species1)
        T_creunlata_b_3 = Equation.objects.create(name='Terminalia crenulata b3', string='0.4186(dbh)^2 - 1.3886(dbh) + 2.4775',\
            owner=self.user, public=True, region=region, species=species1, less_than_ten=True)
        T_crenulata_b_4 = Equation.objects.create(name='Terminalia crenulata b4', string='0.0105(dbh)^2 - 0.0363(dbh) + 0.1030',\
            owner=self.user, public=True, region=region, less_than_ten=True, species=species1)

        T_tomentosa_b_1 = Equation.objects.create(name='T tomentosa b1', string='1815.5165(dbh/100)^3 - 1348.7147(dbh/100)^2 + 594.0835(dbh/100) - 29.0793',
            owner=self.user, public=True, region=region, species=species2)
        T_tomentosa_b_2 = Equation.objects.create(name='T tomentosa b2', string='44.8486(dbh/100)^2 - 8.7590(dbh/100) + 1.2305',
            owner=self.user, public=True, region=region, species=species2)
        T_tomentosa_b_3 = Equation.objects.create(name='T tomentosa b3', string='0.4186(dbh)^2 - 1.3886(dbh) + 2.4775',
            owner=self.user, public=True, region=region, less_than_ten=True, species=species2)
        T_tomentosa_b_4 = Equation.objects.create(name='T tomentosa b3', string='0.0105(dbh)^2 - 0.0363(dbh) + 0.1030',
            owner=self.user, public=True, region=region, less_than_ten=True, species=species2)

        ## Create the project and parcel to test
        project = Project.objects.create(owner=self.user, aeq=Equation.objects.get(id=7), region='India')
        parcel = Parcel.objects.create(project=project, area_reported=100, aeq=Equation.objects.get(id=7))

        plot = Plot.objects.create(project=project, parcel=parcel, area_reported=100, root_shoot_ratio=0.33, aeq=Equation.objects.get(id=7),\
            region=region, calculate_by_species=True, litter_tc_ha=10, deadwood_tc_ha=10, nontree_agb_tc_ha=10, nontree_bgb_tc_ha=10)
        plot.soil_coarse_fragments_ratio = 0.15
        plot.soil_bulk_density = 15
        plot.soil_volume = 15
        plot.soil_mass_oven_sample = 15
        plot.soil_gravimetric_moisture_content = 15
        plot.soil_mass_tin = 15
        plot.soil_mass_oven_subsample = 15
        plot.soil_mass_air_subsample_plus_tin = 15
        plot.soil_mass_air_sample_coarse_fragments = 15
        plot.soil_mass_air_sample = 15
        plot.soil_depth = 15
        plot.soil_carbon_concentration = 0.15
        plot.save()

        Tree.objects.create(plot=plot, genus='Terminalia', species='crenulata', dbh=20.0)
        Tree.objects.create(plot=plot, genus='Terminalia', species='crenulata', dbh=5.0)
        Tree.objects.create(plot=plot, genus='Terminalia', species='tomentosa', dbh=15.0)
        Tree.objects.create(plot=plot, genus='Terminalia', species='tomentosa', dbh=3.0)
        Tree.objects.create(plot=plot, genus='Acacia', species='mearnsu', dbh=6.0)
        Tree.objects.create(plot=plot, genus='Acacia', species='mearnsu', dbh=11.0)

        plot._update_tree_aeq_association()

        print "\--------------------------------------"
        result = calculateTotalCarbonStocks.delay(project.id)
        r = AsyncResult(result.id).ready()
        f = AsyncResult(result.id).failed()
        print "result.backend: %s" % (result.backend)

        #task1 = parcelCalculate(p.id)
        print "AsyncResult(result.id).ready(): %s" % (r)
        print "AsyncResult(result.id).state: %s" % (AsyncResult(result.id).state)
        print "AsyncResult(result.id).result: %s" % (AsyncResult(result.id).result)
        print "AsyncResult(result.id).failed(): %s" % (f)
        print "result.app: %s" % (result.app)
        print "result.id: %s" % (result.id)
        print "--------------------------------------"
        #spin while not ready
        while not r:
            r = AsyncResult(result.id).ready()
            f = AsyncResult(result.id).failed()
            print "AsyncResult(c.id).state: %s" % (AsyncResult(result.id).state)
        #ready!
        print "--------------------------------------"
        print "AsyncResult(result.id).ready(): %s" % (r)
        print "AsyncResult(result.id).state: %s" % (AsyncResult(result.id).state)
        print "AsyncResult(result.id).result: %s" % (AsyncResult(result.id).result)
        print "AsyncResult(result.id).failed(): %s" % (f)
        print "--------------------------------------"

        parcel_stocks = ParcelCarbonStockTierThree.objects.get(parcel=parcel)


        self.assertEqual(int(parcel_stocks.agb_tc), 2467)
        self.assertEqual(int(parcel_stocks.bgb_tc), 1484)
        self.assertEqual(int(parcel_stocks.litter_tc), 1000)
        self.assertEqual(int(parcel_stocks.deadwood_tc), 1000)
        self.assertEqual(int(parcel_stocks.soc_tc), 286875)

        project.delete()
        return True
"""
class TestUpload(TestCase):
    fixtures = ['allometric.json', 'mrvapi.json', 'ecalc.json']
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.factory = RequestFactory

    def test_forms(self):

        workbook_path = "static/documents/Data_Upload_MRV_test.xls"
        workbook = open(workbook_path, 'r')
        root_to_shoot = 0.33
        region = "Western Ghats"
        equation = 2

        form_data = {
                        'workbook': workbook,
                        'root_to_shoot': root_to_shoot,
                        'region': region,
                        'equation': equation,
                    }

        form = BiomassXLSUploadForm(data=form_data)

        self.assertEqual(form.is_valid(), True)
"""

"""
    def test_upload(self):

        #Step 1 - Set Up Project and Form
        request = self.factory.post()


        request.FILES['workbook'] =
        project = Project.objects.create(owner=self.user, name="MRV", aeq=Equation.objects.get(id=7))
        #parcel = Parcel.objects.create(project=project, name="Forest Parcel", area_reported=100, aeq=Equation.objects.get(id=7))
        #plot = Plot.objects.create(parcel=parcel, project=project, root_shoot_ratio=.33, aeq=Equation.objects.get(id=7))

        form = BiomassXLSUploadForm()
        form.workbook = "static/documents/Data_Upload_MRV_test.xls"
        form.root_to_shoot = 0.33
        form.region = "Western Ghats"
        form.equation = 2

        #region_field = form.cleaned_data['region']
        #equation_field = form.cleaned_data['equation']

        # Step 2 - Load workboot object

        f = open(form.workbook, 'r')
        workbook = open_workbook(file_contents=f.read(), encoding_override=workbook_encoding)
        biomassSheet = workbook.sheet_by_name('Plot Data for Upload')"""'''
"""