"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from mrvapi.models import Project, Parcel, Plot, Tree
from allometric.models import Equation, EquationRegion, EquationSpecies
from django.test import TestCase
from measuring.tasks import *
from celery.result import AsyncResult
from django.contrib.auth.models import User
from django.test.runner import DiscoverRunner
from djcelery.contrib.test_runner import _set_eager
from django.test.client import RequestFactory


class TestEquations(TestCase):
	fixtures = ['allometric.json', 'india_biomass.json', 'india_species.json', 'india_volumetric.json','mrvapi.json', 'ecalc.json']
	def setUp(self):
		self.user = User.objects.get(id=1)
		print self.user

	def test_simple_equation(self):
		'''print "TEST SIMPLE EQUATION"
		aeq = Equation.objects.get(id=7)
		print aeq
		proj = Project.objects.create(owner=self.user, aeq=Equation.objects.get(id=7))
		proj.save()
		parcel = Parcel.objects.create(project=proj,area_reported=100,aeq=Equation.objects.get(id=7))
		parcel.save()
		pl = Plot.objects.create(parcel=parcel, project=proj, root_shoot_ratio=.33, aeq=Equation.objects.get(id=7), area_reported=100)
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

		Trees = pl.tree_set.all()
		equations = Equation.objects.all()

		write = "-----------------------Equation Biomass Results---------------"
		write += "Equation Name,Species,Results,Region,pk,string\n"
        
		for eqtn in equations:
			result = calculateTotalCarbonStocks(proj.id)
			project_carbon_stock = ProjectCarbonStock.objects.get(project=proj.id)
			project_carbon_stock.save()
			write += "%s,%s,%s,%s,%s,%s\n" % (eqtn.name, eqtn.species, project_carbon_stock.total_tc, eqtn.region, eqtn.pk, eqtn.string)

		f = open('allometric_test_results.csv', 'w')
		f.write(write)

		print result'''
		return True

