from django.contrib import admin
from mrvapi.models import Project
from models import CarbonPools, LandCover, Parcel, LandUse, Practice, Scenario

class LandCover_Inline(admin.TabularInline):
    model = LandCover
    extra = 1
    show_edit_link = True
    
class Parcel_Inline(admin.TabularInline):
    model = Parcel
    extra = 1

class LandUse_Inline(admin.TabularInline):
    model = LandUse
    extra = 1

# class Project_Admin(admin.ModelAdmin):
#     inlines = [LandCover_Inline]
#     list_display = ('name','duration','continent','climate_zone','moisture_zone','soil_type')
#     list_editable = ('duration','continent','climate_zone','moisture_zone','soil_type')
#     fieldsets = (
#         (None,{'fields':(('name','user'),) }),
#         ('Parcel Defaults',{'fields':(('continent', 'climate_zone'),('moisture_zone', 'soil_type'))}),
#         ('Constants',{'fields':('cdm',)}) )
#     #def get_form(self, request, obj=None, **kwargs):
#        # form = super(Project_Admin,self).get_form(self,request, obj,**kwargs)
#         #form.base_fields['user'].queryset = form.base_fields['user'].queryset.filter(user=request.user)
#         #return form
# admin.site.register(Project, Project_Admin)

class LandCover_Admin(admin.ModelAdmin):
    name = "Land Cover"
    list_display = ('name', 'category','biomassa','biomassb',
        'litter','dead_wood','soil')
    list_editable = ('category','biomassa','biomassb',
        'litter','dead_wood','soil')
admin.site.register(LandCover, LandCover_Admin)

class Practice_Admin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields':('name','project','harvest','burn','agricultural_practices')}),
              #('use_prescribed_accum','prescribed_accum'),
              #'cultivation_period','agricultural_practices')}),
    )
    filter_horizontal = ('agricultural_practices',)
admin.site.register(Practice, Practice_Admin)

class Parcel_Admin(admin.ModelAdmin):
    list_display = ('name','initial_lc','location','area')
admin.site.register(Parcel, Parcel_Admin)

class Scenario_Admin(admin.ModelAdmin):
    inlines = [LandUse_Inline]
    fieldsets = (
        (None,{'fields':('name','parcel','reference_scenario')}),)
admin.site.register(Scenario, Scenario_Admin)

class CarbonPools_Admin(admin.ModelAdmin):
    list_display = ('scenario', 'year', 'GetBiomass', 'GetDeadCarbon', 'GetSoil',
        'GetAtmCarbon','GetAtmCH4','GetAtmN2O','GetHarvested')
admin.site.register(CarbonPools, CarbonPools_Admin)

from ipcc import *

class Aboveground_Biomass_Admin(admin.ModelAdmin):
    name = "Aboveground Biomass"
    list_display = ('name','continent','biome','managed','value','units')
admin.site.register(Aboveground_Biomass,Aboveground_Biomass_Admin)

class Necromass_Admin(admin.ModelAdmin):
    list_display = ('climate','litterC','deadwoodC','units')
admin.site.register(Necromass, Necromass_Admin)

class Belowground_Ratio_Admin(admin.ModelAdmin):
    list_display = ('biome','category','value')
admin.site.register(Belowground_Ratio, Belowground_Ratio_Admin)

class Combustion_Factor_Admin(admin.ModelAdmin):
    list_display = ('biome','pctReleased','emissCO2','emissCH4','emissN2O')
admin.site.register(Combustion_Factor)
admin.site.register(Land_Use)

class Combustion_Land_Use_Admin(admin.ModelAdmin):
    list_display = ('land_use','pctReleased','emissCO2','emissCH4','emissN2O')
admin.site.register(Combustion_Land_Use, Combustion_Land_Use_Admin)

class Biomass_Land_Use_Admin(admin.ModelAdmin):
    list_display = ('climate','land_use','previousOrFinal','value','age')
admin.site.register(Biomass_Land_Use,Biomass_Land_Use_Admin)

class Soil_Carbon_Ref_Admin(admin.ModelAdmin):
    list_display = ('soil_type','climate','value')
admin.site.register(Soil_Carbon_Ref, Soil_Carbon_Ref_Admin)
class Soil_Carbon_Factor_Admin(admin.ModelAdmin):
    list_display = ('land_use','climate','value')
admin.site.register(Soil_Carbon_Factor, Soil_Carbon_Factor_Admin)

#admin.site.register(Agricultural_Practice)
#admin.site.register(Agriculture_Carbon_Stored)
#admin.site.register(Forest_Growth)

class Rice_Practice_Admin(admin.ModelAdmin):
    list_display = ('name','type')

admin.site.register(Rice_Practice, Rice_Practice_Admin)
admin.site.register(Rice_Emission)
admin.site.register(Grassland_Soil)
admin.site.register(Grassland_Biomass)