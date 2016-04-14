from django.test import TestCase
from mrvapi.models import Project, Parcel, Plot


class TestEcalc(TestCase):
	def setUp(self):
        self.user = User.objects.get(id=1)
    def test_emissions_cal(self):
		project = Project.objects.create(owner=self.user, name="test project",aeq=Equation.objects.get(id=7))
	    parcel = Parcel.objects.create(project=project,area_reported=100,aeq=Equation.objects.get(id=7))
	    plot = Plot.objects.create(parcel=p, project=project, root_shoot_ratio=.33, aeq=Equation.objects.get(id=7), area_reported=100)
	    plot.save()
	    self.failUnlessEqual()

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


