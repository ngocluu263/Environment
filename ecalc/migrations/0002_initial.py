# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("mrvapi","0001_initial"),
    )
    def forwards(self, orm):
        # Adding model 'Continent'
        # Adding model 'LandCover'
        db.create_table(u'ecalc_landcover', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mrvapi.Project'])),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('biomassa', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('biomassb', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('litter', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('dead_wood', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('soil', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('combustion_pctreleased', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('CH4', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('N2O', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('young_growth_rate', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('old_growth_rate', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('biomassratio', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'ecalc', ['LandCover'])

        # Adding model 'Practice'
        db.create_table(u'ecalc_practice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mrvapi.Project'])),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('harvest', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('burn', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'ecalc', ['Practice'])

        # Adding M2M table for field agricultural_practices on 'Practice'
        m2m_table_name = db.shorten_name(u'ecalc_practice_agricultural_practices')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('practice', models.ForeignKey(orm[u'ecalc.practice'], null=False)),
            ('agricultural_practice', models.ForeignKey(orm[u'ecalc.agricultural_practice'], null=False))
        ))
        db.create_unique(m2m_table_name, ['practice_id', 'agricultural_practice_id'])

        # Adding model 'Parcel'
        db.create_table(u'ecalc_parcel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ecalc_parcel_set', to=orm['mrvapi.Project'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('area', self.gf('django.db.models.fields.FloatField')()),
            ('initial_lc', self.gf('django.db.models.fields.related.ForeignKey')(related_name='initial', to=orm['ecalc.LandCover'])),
        ))
        db.send_create_signal(u'ecalc', ['Parcel'])

        # Adding model 'Scenario'
        db.create_table(u'ecalc_scenario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mrvapi.Project'])),
            ('parcel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecalc.Parcel'], null=True)),
            ('reference_scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecalc.Scenario'], null=True)),
        ))
        db.send_create_signal(u'ecalc', ['Scenario'])

        # Adding model 'LandUse'
        db.create_table(u'ecalc_landuse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('landcover', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecalc.LandCover'], null=True, blank=True)),
            ('start_year', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecalc.Scenario'])),
            ('adoption', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('degraded', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('prior_harvest', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('prior_burn', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('practice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecalc.Practice'])),
        ))
        db.send_create_signal(u'ecalc', ['LandUse'])

        # Adding model 'CarbonPools'
        db.create_table(u'ecalc_carbonpools', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('scenario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecalc.Scenario'])),
            ('landcover', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecalc.LandCover'])),
            ('age', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('biomassa', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('biomassb', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('litter', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('dead_wood', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('soil', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('dsoil', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('atm_carbon', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('atm_ch4', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('atm_n2o', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('annual_emissions', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('annual_nonco2', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('harvested', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'ecalc', ['CarbonPools'])


    def backwards(self, orm):
        # Removing unique constraint on 'Grassland_Soil', fields ['status', 'climate']
        db.delete_unique(u'ecalc_grassland_soil', ['status', 'climate_id'])

        # Removing unique constraint on 'Forest_Growth', fields ['managed', 'continent', 'biome', 'youngOrOld']
        db.delete_unique(u'ecalc_forest_growth', ['managed', 'continent_id', 'biome_id', 'youngOrOld'])

        # Removing unique constraint on 'Agriculture_Carbon_Stored', fields ['agricultural_practice', 'simple_climate']
        db.delete_unique(u'ecalc_agriculture_carbon_stored', ['agricultural_practice_id', 'simple_climate_id'])

        # Removing unique constraint on 'Soil_Carbon_Ref', fields ['soil_type', 'climate']
        db.delete_unique(u'ecalc_soil_carbon_ref', ['soil_type_id', 'climate_id'])

        # Removing unique constraint on 'Soil_Carbon_Factor', fields ['land_use', 'climate']
        db.delete_unique(u'ecalc_soil_carbon_factor', ['land_use_id', 'climate_id'])

        # Removing unique constraint on 'Biomass_Land_Use', fields ['land_use', 'climate', 'previousOrFinal']
        db.delete_unique(u'ecalc_biomass_land_use', ['land_use_id', 'climate_id', 'previousOrFinal'])

        # Removing unique constraint on 'Belowground_Ratio', fields ['biome', 'category']
        db.delete_unique(u'ecalc_belowground_ratio', ['biome_id', 'category'])

        # Removing unique constraint on 'Aboveground_Biomass', fields ['managed', 'continent', 'biome']
        db.delete_unique(u'ecalc_aboveground_biomass', ['managed', 'continent_id', 'biome_id'])

        # Removing unique constraint on 'Climate', fields ['climate_zone', 'moisture_zone']
        db.delete_unique(u'ecalc_climate', ['climate_zone_id', 'moisture_zone_id'])

        # Deleting model 'Continent'
        db.delete_table(u'ecalc_continent')

        # Deleting model 'Climate_Zone'
        db.delete_table(u'ecalc_climate_zone')

        # Deleting model 'Moisture_Zone'
        db.delete_table(u'ecalc_moisture_zone')

        # Deleting model 'Soil_Type'
        db.delete_table(u'ecalc_soil_type')

        # Deleting model 'GWP'
        db.delete_table(u'ecalc_gwp')

        # Deleting model 'Biome'
        db.delete_table(u'ecalc_biome')

        # Deleting model 'Simple_Climate'
        db.delete_table(u'ecalc_simple_climate')

        # Deleting model 'Climate'
        db.delete_table(u'ecalc_climate')

        # Deleting model 'Aboveground_Biomass'
        db.delete_table(u'ecalc_aboveground_biomass')

        # Deleting model 'Necromass'
        db.delete_table(u'ecalc_necromass')

        # Deleting model 'Belowground_Ratio'
        db.delete_table(u'ecalc_belowground_ratio')

        # Deleting model 'Combustion_Factor'
        db.delete_table(u'ecalc_combustion_factor')

        # Deleting model 'Land_Use'
        db.delete_table(u'ecalc_land_use')

        # Deleting model 'Combustion_Land_Use'
        db.delete_table(u'ecalc_combustion_land_use')

        # Deleting model 'Biomass_Land_Use'
        db.delete_table(u'ecalc_biomass_land_use')

        # Deleting model 'Soil_Carbon_Factor'
        db.delete_table(u'ecalc_soil_carbon_factor')

        # Deleting model 'Soil_Carbon_Ref'
        db.delete_table(u'ecalc_soil_carbon_ref')

        # Deleting model 'Agricultural_Practice'
        db.delete_table(u'ecalc_agricultural_practice')

        # Deleting model 'Agriculture_Carbon_Stored'
        db.delete_table(u'ecalc_agriculture_carbon_stored')

        # Deleting model 'Forest_Growth'
        db.delete_table(u'ecalc_forest_growth')

        # Deleting model 'Rice_Practice'
        db.delete_table(u'ecalc_rice_practice')

        # Deleting model 'Rice_Emission'
        db.delete_table(u'ecalc_rice_emission')

        # Deleting model 'Grassland_Soil'
        db.delete_table(u'ecalc_grassland_soil')

        # Deleting model 'Grassland_Biomass'
        db.delete_table(u'ecalc_grassland_biomass')

        # Deleting model 'LandCover'
        db.delete_table(u'ecalc_landcover')

        # Deleting model 'Practice'
        db.delete_table(u'ecalc_practice')

        # Removing M2M table for field agricultural_practices on 'Practice'
        db.delete_table(db.shorten_name(u'ecalc_practice_agricultural_practices'))

        # Deleting model 'Parcel'
        db.delete_table(u'ecalc_parcel')

        # Deleting model 'Scenario'
        db.delete_table(u'ecalc_scenario')

        # Deleting model 'LandUse'
        db.delete_table(u'ecalc_landuse')

        # Deleting model 'CarbonPools'
        db.delete_table(u'ecalc_carbonpools')


    models = {
        u'allometric.equation': {
            'Meta': {'object_name': 'Equation'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'less_or_equal': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'public': ('django.db.models.fields.BooleanField', [], {}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.EquationRegion']", 'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.EquationSpecies']", 'null': 'True', 'blank': 'True'}),
            'string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'volumetric': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
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
