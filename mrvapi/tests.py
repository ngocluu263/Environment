"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from mrvapi.models import Project, Parcel, Plot, Tree


class LandCoverTests(TestCase):
	def testLandCover(self):
		"""
		Test that land covers are generated with a new project
		"""
		project = Project.objects.create(owner=self.user, aeq=Equation.objects.get(id=7))


class TestModels(TestCase):
    def setUp(self):
        """
        Tests that parcels are being created properly.
        """
        ModelFactory = ModelFactory()
        self.project1 = ModelFactory.createProject()
        self.parcel1 = ModelFactory.createParcel(project1)

    def checkProject(self):
        """
        Check if the values below exist.
        """
        project1 = self.project1
        self.assertTrue(project1.reported_area)
        self.assertTrue(project1.aeq)
        self.assertTrue(project1.continent)
        self.assertTrue(project1.climate_zone)
        self.assertTrue(project1.moisture_zone)
        self.assertTrue(project1.soil_type)
        self.assertTrue(proejct1.cdm)

    def checkParcel(self):
        """
        Check if the values below exist.
        """
        parcel = self.parcel1
        self.assertTrue(parcel.name)
        self.assertTrue(parcel.poly_mapped)
        self.assertTrue(parcel.poly_reported)
        self.assertTrue(parcel.aeq)
        # T1
        self.assertTrue(parcel.t1_agb)
        self.assertTrue(parcel.t1_bgb)
        self.assertTrue(parcel.t1_soc)
        self.assertTrue(parcel.t1_deadwood)
        self.assertTrue(parcel.t1_litter)
        #T2
        self.assertTrue(parcel.t2_agb)
        self.assertTrue(parcel.t2_bgb)
        self.assertTrue(parcel.t2_soc)
        self.assertTrue(parcel.t2_deadwood)
        self.assertTrue(parcel.t2_litter)

    def checkProjectPermissions(self):
        """
        Checks if project permissions are being saved correctly.
        """
        pass
		

class ModelFactory():
    user = User.objects.get(id=1)


    def createProject(self):
        project = Project(owner=self.user, name="test", region="Asia (indian subcontinental)", counry="India")
        project.save()
        return project

    def createParcel(self, proj):

        parcel = Parcel(project=proj)
        parcel.save()
        return parcel

    def createPlot(self, parcel):
        plot = Plot(project=parcel.project, parcel=parcel)
        plot.save()
        return plot

    def createTree(self, plot):
        tree = Tree(plot=plot)
        tree.save()
        return tree
