# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'allometric.equation': {
            'Meta': {'object_name': 'Equation'},
            'anatomy': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.EquationCategory']", 'null': 'True'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latex': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'less_than_ten': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'public': ('django.db.models.fields.BooleanField', [], {}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.EquationRegion']", 'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.EquationSpecies']", 'null': 'True', 'blank': 'True'}),
            'string': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'volumetric': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'allometric.equationcategory': {
            'Meta': {'object_name': 'EquationCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'allometric.equationcountry': {
            'Meta': {'object_name': 'EquationCountry'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'allometric.equationregion': {
            'Meta': {'object_name': 'EquationRegion'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.EquationCountry']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'allometric.equationspecies': {
            'Meta': {'object_name': 'EquationSpecies'},
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'genus': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.EquationRegion']", 'null': 'True', 'blank': 'True'}),
            'wood_gravity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ecalc.aboveground_biomass': {
            'Meta': {'unique_together': "(('managed', 'continent', 'biome'),)", 'object_name': 'Aboveground_Biomass'},
            'biome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Biome']"}),
            'continent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Continent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'managed': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.agricultural_practice': {
            'Meta': {'object_name': 'Agricultural_Practice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'ecalc.agriculture_carbon_stored': {
            'Meta': {'unique_together': "(('agricultural_practice', 'simple_climate'),)", 'object_name': 'Agriculture_Carbon_Stored'},
            'agricultural_practice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Agricultural_Practice']"}),
            'amountC': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'simple_climate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Simple_Climate']"})
        },
        u'ecalc.belowground_ratio': {
            'Meta': {'unique_together': "(('biome', 'category'),)", 'object_name': 'Belowground_Ratio'},
            'biome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Biome']"}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.biomass_land_use': {
            'Meta': {'unique_together': "(('land_use', 'climate', 'previousOrFinal'),)", 'object_name': 'Biomass_Land_Use'},
            'age': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'climate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_use': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Land_Use']"}),
            'previousOrFinal': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.biome': {
            'Meta': {'object_name': 'Biome'},
            'climate_zone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate_Zone']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        u'ecalc.carbonpools': {
            'Meta': {'ordering': "['year']", 'object_name': 'CarbonPools'},
            'age': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'annual_emissions': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'annual_nonco2': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'atm_carbon': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'atm_ch4': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'atm_n2o': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biomassa': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biomassb': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'dead_wood': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'dsoil': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'harvested': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'landcover': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.LandCover']"}),
            'litter': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Scenario']"}),
            'soil': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'ecalc.climate': {
            'Meta': {'unique_together': "(('climate_zone', 'moisture_zone'),)", 'object_name': 'Climate'},
            'climate_zone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate_Zone']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moisture_zone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Moisture_Zone']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'simple_climate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Simple_Climate']", 'null': 'True'})
        },
        u'ecalc.climate_zone': {
            'Meta': {'object_name': 'Climate_Zone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'})
        },
        u'ecalc.combustion_factor': {
            'Meta': {'object_name': 'Combustion_Factor'},
            'biome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Biome']"}),
            'emissCH4': ('django.db.models.fields.FloatField', [], {}),
            'emissCO2': ('django.db.models.fields.FloatField', [], {}),
            'emissN2O': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pctReleased': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.combustion_land_use': {
            'Meta': {'object_name': 'Combustion_Land_Use'},
            'emissCH4': ('django.db.models.fields.FloatField', [], {}),
            'emissCO2': ('django.db.models.fields.FloatField', [], {}),
            'emissN2O': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_use': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Land_Use']"}),
            'pctReleased': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.continent': {
            'Meta': {'object_name': 'Continent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'})
        },
        u'ecalc.forest_growth': {
            'Meta': {'unique_together': "(('managed', 'continent', 'biome', 'youngOrOld'),)", 'object_name': 'Forest_Growth'},
            'biome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Biome']"}),
            'continent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Continent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'managed': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'youngOrOld': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'ecalc.grassland_biomass': {
            'Meta': {'object_name': 'Grassland_Biomass'},
            'climate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.grassland_soil': {
            'Meta': {'unique_together': "(('status', 'climate'),)", 'object_name': 'Grassland_Soil'},
            'climate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.gwp': {
            'Meta': {'object_name': 'GWP'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        u'ecalc.land_use': {
            'Meta': {'object_name': 'Land_Use'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        u'ecalc.landcover': {
            'CH4': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'Meta': {'ordering': "['name']", 'object_name': 'LandCover'},
            'N2O': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biomassa': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biomassb': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biomassratio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'combustion_pctreleased': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'dead_wood': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'litter': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'old_growth_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mrvapi.Project']"}),
            'soil': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'young_growth_rate': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'ecalc.landuse': {
            'Meta': {'object_name': 'LandUse'},
            'adoption': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'degraded': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'landcover': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.LandCover']", 'null': 'True', 'blank': 'True'}),
            'practice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Practice']"}),
            'prior_burn': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prior_harvest': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Scenario']"}),
            'start_year': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'ecalc.moisture_zone': {
            'Meta': {'object_name': 'Moisture_Zone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'})
        },
        u'ecalc.necromass': {
            'Meta': {'object_name': 'Necromass'},
            'climate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate']", 'unique': 'True'}),
            'deadwoodC': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'litterC': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'ecalc.parcel': {
            'Meta': {'object_name': 'Parcel'},
            'area': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_lc': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'initial'", 'to': u"orm['ecalc.LandCover']"}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ecalc_parcel_set'", 'to': u"orm['mrvapi.Project']"})
        },
        u'ecalc.practice': {
            'Meta': {'object_name': 'Practice'},
            'agricultural_practices': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['ecalc.Agricultural_Practice']", 'null': 'True', 'blank': 'True'}),
            'burn': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'harvest': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mrvapi.Project']"})
        },
        u'ecalc.rice_emission': {
            'Meta': {'object_name': 'Rice_Emission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rice_practice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Rice_Practice']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.rice_practice': {
            'Meta': {'object_name': 'Rice_Practice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'ecalc.scenario': {
            'Meta': {'object_name': 'Scenario'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'landcovers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ecalc.LandCover']", 'through': u"orm['ecalc.LandUse']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'parcel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Parcel']", 'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mrvapi.Project']"}),
            'reference_scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Scenario']", 'null': 'True'})
        },
        u'ecalc.simple_climate': {
            'Meta': {'object_name': 'Simple_Climate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        u'ecalc.soil_carbon_factor': {
            'Meta': {'unique_together': "(('land_use', 'climate'),)", 'object_name': 'Soil_Carbon_Factor'},
            'climate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_use': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Land_Use']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'ecalc.soil_carbon_ref': {
            'Meta': {'unique_together': "(('soil_type', 'climate'),)", 'object_name': 'Soil_Carbon_Ref'},
            'climate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'soil_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Soil_Type']"}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'ecalc.soil_type': {
            'Meta': {'object_name': 'Soil_Type'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'})
        },
        u'mrvapi.project': {
            'Meta': {'object_name': 'Project'},
            'abstract': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'aeq': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.Equation']", 'null': 'True'}),
            'cdm': ('django.db.models.fields.FloatField', [], {'default': '0.47'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'climate_zone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Climate_Zone']", 'null': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'continent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Continent']", 'null': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'country_address': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '50', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moisture_zone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Moisture_Zone']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'reported_area': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'soil_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ecalc.Soil_Type']", 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'})
        }
    }

    complete_apps = ['ecalc']
    symmetrical = True
