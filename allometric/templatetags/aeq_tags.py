###############################################################################
#
#   File: aeq_tags.py
#   Module: allometric
#   Author: Chelsea Bridson
#   -------------------------------
#
#   Purpose:  template tags for the aeq list
#
###############################################################################

from django import template
from django.template.defaultfilters import stringfilter
from allometric.models import *
import re

register = template.Library()

@register.filter(name='TeX')
@stringfilter
#   Converts a regular math string into a latex expression
#   Input: 8x^2/x^4
#   Output: |frac{8x^2}{x^4}
def TeX(aeq_string, eqtn_type):

	eqtn_type = eqtn_type.split(',')
	less_than_ten = eqtn_type[1]
	eqtn_type = eqtn_type[0]
#COPY BELOW THIS LINE

	#Remove whitespace
	eqtn = "".join(aeq_string.split())

	#Are there parenthesis around the entire equation?
	match = re.match(r"^\((.+)\)$", eqtn)
	if match:
		eqtn = "^^%s$$" % (m.group(1))

	eqtn = re.sub(r'exp\((-*\w+\.*\w*)\)', r'e^{(\1)}', eqtn)
	#(.)^(.) >> (.)^{.}
	result = re.sub(r'\((.*)\)^\((.*)\)', r'\(\1\)^\{\2\}', eqtn)
	#^(\1) >> ^{(\1)}
	result = re.sub(r'\^\((\w+/*\.*\w*)\)', r'^{(\1)}', result)

	dfrac = re.sub(r'(dbh/100)', r'\\frac{D_{BH}}{100}', result)
	sqrt = re.sub(r'sqrt\({1}(.+)\){1}', r'\\sqrt{\1}', dfrac)
	dbh = re.sub(r'dbh', r'D_{BH}', sqrt)
	pi = re.sub(r'pi', r'\\pi', dbh)
	total_height = re.sub(r'total_height', r'\\text{total_height}', pi)
	crown_d_max = re.sub(r'crown_d_max', r'\\text{crown_d_max}', total_height)
	crown_d_90 = re.sub(r'crown_d_90', r'\\text{crown_d_90}', crown_d_max)
	wood_gravity = re.sub(r'wood_gravity', r'\\text{wood_gravity}', crown_d_90)

	text2 = "%s" % (wood_gravity) #\\[ \\]

	return text2

@register.filter(name='TeX3')
@stringfilter
def TeX3(aeq_string):
	#Remove whitespace
	eqtn = "".join(aeq_string.split())

	#Are there parenthesis around the entire equation?
	match = re.match(r"^\((.+)\)$", eqtn)
	if match:
		eqtn = "^^%s$$" % (m.group(1))
	eqtn = re.sub(r'exp\((-*\w+\.*\w*)\)', r'e^{(\1)}', eqtn)
	result = re.sub(r'\((.*)\)^\((.*)\)', r'\(\1\)^\{\2\}', eqtn)
	result = re.sub(r'\^\((\w+/*\.*\w*)\)', r'^{(\1)}', result)

	dfrac = re.sub(r'(dbh/100)', r'\\frac{D_{BH}}{100}', result)
	sqrt = re.sub(r'sqrt\({1}(.+)\){1}', r'\\sqrt{\1}', dfrac)
	dbh = re.sub(r'dbh', r'D_{BH}', sqrt)
	pi = re.sub(r'pi', r'\\pi', dbh)
	total_height = re.sub(r'total_height', r'\\text{total_height}', pi)
	crown_d_max = re.sub(r'crown_d_max', r'\\text{crown_d_max}', total_height)
	crown_d_90 = re.sub(r'crown_d_90', r'\\text{crown_d_90}', crown_d_max)
	wood_gravity = re.sub(r'wood_gravity', r'\\text{wood_gravity}', crown_d_90)
	frac = re.sub(r'\(([^)])/([^)])\)', r'\\frac{\1}{\2}', wood_gravity)

	text2 = "$%s$" % (frac) #\\[ \\]

	return text2

@register.filter(name='nameBreak')
@stringfilter
def nameBreak(name_string):
  name_string = name_string.replace("(", "\n(")
  return name_string


class EquationsForRegionNode(template.Node):
	def __init__(self, title, region):
		self.region = template.Variable(region)
		self.species = template.Variable(title)

	def render(self, context):

		region = self.region.resolve(context)
		species = self.species.resolve(context)

		genus_name = species.split()


		sp = EquationSpecies.objects.get(name=genus_name[1], genus=genus_name[0])
		rg = EquationRegion.objects.get(name=region)
		rg_pk = rg.pk
		sp_pk = sp.pk

		equations = Equation.objects.filter(region=rg_pk, species=sp_pk)
		volumetric = False

		if equations:
			context['equations'] = equations
			volumetric = equations.filter(volumetric=True)

		else:
			context['equations'] = None

		if volumetric:
			context['volumetric'] = volumetric[0]

		nonvolumetric_equations = equations.filter(volumetric=False)
		if nonvolumetric_equations:
			context['nonvolumetric_equations'] = nonvolumetric_equations

			less_than_10_SW = equations.filter(anatomy="SW", less_than_ten=True)
			if less_than_10_SW:
				context['less_than_10_SW'] = less_than_10_SW[0]
			else:
				context['less_than_10_SW'] = None

			less_than_10_FL = equations.filter(anatomy="FL", less_than_ten=True)
			if less_than_10_FL:
				context['less_than_10_FL'] = less_than_10_FL[0]
			else:
				context['less_than_10_FL'] = None

			if less_than_10_FL or less_than_10_SW:
				less_than_10 = equations.filter(less_than_ten=True)
				context['less_than_10'] = less_than_10
			else:
				context['less_than_10'] = None

			more_than_10_SW = equations.filter(anatomy="SW", less_than_ten=False)
			if more_than_10_SW:
				context['more_than_10_SW'] = more_than_10_SW[0]
			else:
				context['more_than_10_SW'] = None

			more_than_10_FL = equations.filter(anatomy="FL", less_than_ten=False)
			if more_than_10_FL:
				context['more_than_10_FL'] = more_than_10_FL[0]
			else:
				context['more_than_10_FL'] = None

			if more_than_10_FL or more_than_10_SW:
				more_than_10 = equations.filter(less_than_ten=False)
				context['more_than_10'] = more_than_10
			else:
				context['more_than_10'] = None

		else:
			context['nonvolumetric_equations'] = None

		return ''

@register.tag
def get_equations_for_region(parser, token):
	tag_name, species, region  = token.split_contents()
	return EquationsForRegionNode(species, region)
