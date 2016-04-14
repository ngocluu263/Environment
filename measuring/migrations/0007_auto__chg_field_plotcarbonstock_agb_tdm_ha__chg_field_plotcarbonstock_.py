# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PlotCarbonStock.agb_tdm_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'agb_tdm_ha', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.bgb_tc_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'bgb_tc_ha', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.agb_tc_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'agb_tc_ha', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.dbh_sd'
        db.alter_column(u'measuring_plotcarbonstock', 'dbh_sd', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.wsg_sd'
        db.alter_column(u'measuring_plotcarbonstock', 'wsg_sd', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.height_sd'
        db.alter_column(u'measuring_plotcarbonstock', 'height_sd', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.estimated_n_trees'
        db.alter_column(u'measuring_plotcarbonstock', 'estimated_n_trees', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.wsg_mean'
        db.alter_column(u'measuring_plotcarbonstock', 'wsg_mean', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.trees_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'trees_ha', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.height_mean'
        db.alter_column(u'measuring_plotcarbonstock', 'height_mean', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.dbh_mean'
        db.alter_column(u'measuring_plotcarbonstock', 'dbh_mean', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'PlotCarbonStock.bgb_tdm_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'bgb_tdm_ha', self.gf('django.db.models.fields.FloatField')(null=True))

    def backwards(self, orm):

        # Changing field 'PlotCarbonStock.agb_tdm_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'agb_tdm_ha', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.bgb_tc_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'bgb_tc_ha', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.agb_tc_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'agb_tc_ha', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.dbh_sd'
        db.alter_column(u'measuring_plotcarbonstock', 'dbh_sd', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.wsg_sd'
        db.alter_column(u'measuring_plotcarbonstock', 'wsg_sd', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.height_sd'
        db.alter_column(u'measuring_plotcarbonstock', 'height_sd', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.estimated_n_trees'
        db.alter_column(u'measuring_plotcarbonstock', 'estimated_n_trees', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PlotCarbonStock.wsg_mean'
        db.alter_column(u'measuring_plotcarbonstock', 'wsg_mean', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.trees_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'trees_ha', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.height_mean'
        db.alter_column(u'measuring_plotcarbonstock', 'height_mean', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.dbh_mean'
        db.alter_column(u'measuring_plotcarbonstock', 'dbh_mean', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'PlotCarbonStock.bgb_tdm_ha'
        db.alter_column(u'measuring_plotcarbonstock', 'bgb_tdm_ha', self.gf('django.db.models.fields.FloatField')())

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
        u'ecalc.climate_zone': {
            'Meta': {'object_name': 'Climate_Zone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'})
        },
        u'ecalc.continent': {
            'Meta': {'object_name': 'Continent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'})
        },
        u'ecalc.moisture_zone': {
            'Meta': {'object_name': 'Moisture_Zone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'})
        },
        u'ecalc.soil_type': {
            'Meta': {'object_name': 'Soil_Type'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'})
        },
        u'measuring.imagemodel': {
            'Meta': {'object_name': 'ImageModel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'plot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mrvapi.Plot']"})
        },
        u'measuring.parcelcarbonstocktierthree': {
            'Meta': {'object_name': 'ParcelCarbonStockTierThree'},
            'area_used': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'data_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_95_agb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'max_95_bgb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'max_95_deadwood_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'max_95_litter_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'max_95_soc_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'mean_agb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'mean_agb_tdm_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'mean_bgb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'mean_bgb_tdm_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'mean_deadwood_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'mean_litter_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'mean_soc_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'mean_trees_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'min_95_agb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'min_95_bgb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'min_95_deadwood_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'min_95_litter_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'min_95_soc_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'n_plots_agb': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_plots_bgb': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_plots_deadwood': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_plots_litter': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_plots_soc': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parcel': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mrvapi.Parcel']", 'unique': 'True'}),
            'perc_95_agb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'perc_95_bgb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'perc_95_deadwood_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'perc_95_litter_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'perc_95_soc_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'projectCarbonStock': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['measuring.ProjectCarbonStock']"}),
            'std_agb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'std_agb_tdm_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'std_bgb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'std_bgb_tdm_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'std_deadwood_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'std_litter_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'std_soc_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'std_trees_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'measuring.plotcarbonstock': {
            'Meta': {'object_name': 'PlotCarbonStock'},
            'agb_tc_ha': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'agb_tdm_ha': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'bgb_tc_ha': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'bgb_tdm_ha': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'data_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dbh_mean': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'dbh_sd': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'deadwood_tc_ha': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'estimated_n_trees': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'height_mean': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'height_sd': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'litter_tc_ha': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'parcelCarbonStock': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['measuring.ParcelCarbonStockTierThree']"}),
            'plot': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mrvapi.Plot']", 'unique': 'True'}),
            'soc_tc_ha': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'trees_ha': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'wsg_mean': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'wsg_sd': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'measuring.projectcarbonstock': {
            'Meta': {'object_name': 'ProjectCarbonStock'},
            'agb_tc': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '4'}),
            'bgb_tc': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '4'}),
            'data_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deadwood_tc': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'litter_tc': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '4'}),
            'project': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mrvapi.Project']", 'unique': 'True'}),
            'soc_tc': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '4'}),
            'total_area_used': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '4'}),
            'total_tc': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '4'})
        },
        u'mrvapi.parcel': {
            'Meta': {'object_name': 'Parcel'},
            'aeq': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.Equation']", 'null': 'True'}),
            'area_mapped': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'area_reported': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'poly_mapped': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'poly_reported': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'post_resource_identifier': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mrvapi.Project']"}),
            't1_agb': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't1_bgb': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't1_deadwood': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't1_litter': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't1_soc': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't2_agb': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't2_bgb': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't2_deadwood': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't2_litter': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            't2_soc': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'mrvapi.plot': {
            'Meta': {'object_name': 'Plot'},
            'aeq': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.Equation']", 'null': 'True'}),
            'area_mapped': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'area_reported': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'calculate_by_species': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'deadwood_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'dimensions_mapped': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'dimensions_reported': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'elevation': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'gps_latitude': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'gps_longitude': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'hemi_photo_center': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'hemi_photo_east': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'hemi_photo_north': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'hemi_photo_south': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'hemi_photo_west': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'horiz_photo_east': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'horiz_photo_north': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'horiz_photo_south': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'horiz_photo_west': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'litter_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'nontree_agb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'nontree_bgb_tc_ha': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'parcel': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['mrvapi.Parcel']", 'null': 'True', 'blank': 'True'}),
            'poly_mapped': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'poly_reported': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mrvapi.Project']", 'null': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['allometric.EquationRegion']", 'null': 'True'}),
            'root_shoot_ratio': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'sample_crew': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True'}),
            'sample_date': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sample_end_time': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sample_start_time': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'shape_mapped': ('django.db.models.fields.CharField', [], {'default': "'polygon'", 'max_length': '15', 'null': 'True'}),
            'shape_reported': ('django.db.models.fields.CharField', [], {'default': "'polygon'", 'max_length': '15', 'null': 'True'}),
            'slope_condition': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'soil_bulk_density': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_carbon_concentration': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_coarse_fragments_ratio': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_crew': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'soil_date': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'soil_depth': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_end_time': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'soil_gravimetric_moisture_content': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_mass_air_sample': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_mass_air_sample_coarse_fragments': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_mass_air_subsample_plus_tin': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_mass_oven_sample': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_mass_oven_subsample': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_mass_tin': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'soil_serial_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'soil_start_time': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'soil_volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_1_area_m2': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_1_lower_bound': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_1_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'subplot_1_upper_bound': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_2_area_m2': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_2_lower_bound': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_2_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'subplot_2_upper_bound': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_3_area_m2': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_3_lower_bound': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subplot_3_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'subplot_3_upper_bound': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'utm_vertices_mapped': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'utm_vertices_reported': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'weather': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
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

    complete_apps = ['measuring']