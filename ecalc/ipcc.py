from django.db import models

class Continent(models.Model):
    name = models.CharField(max_length=80, unique=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "Continent"
        verbose_name_plural = "Continent"

class Climate_Zone(models.Model):
    name = models.CharField(max_length=80, unique=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "ClimateZone"
        verbose_name_plural = "ClimateZone"

class Moisture_Zone(models.Model):
    name = models.CharField(max_length=80, unique=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "MoistureZone"
        verbose_name_plural = "MoistureZone"

class Soil_Type(models.Model):
    name = models.CharField(max_length=80, unique=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "SoilType"
        verbose_name_plural = "SoilType"

class GWP(models.Model):
    name = models.CharField(max_length=80, unique=True)
    def __unicode__(self):
        return self.name

class Biome(models.Model):
    name = models.CharField(max_length=80, unique=True)
    climate_zone = models.ForeignKey(Climate_Zone)
    def __unicode__(self):
        return self.name

class Simple_Climate(models.Model):
    name = models.CharField(max_length=80, unique=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "SimpleClimate"
        verbose_name_plural = "SimpleClimate"

class Climate(models.Model):
    name = models.CharField(max_length=80, unique=True)
    climate_zone = models.ForeignKey(Climate_Zone, null=True)
    moisture_zone = models.ForeignKey(Moisture_Zone, null=True)
    simple_climate = models.ForeignKey(Simple_Climate, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        unique_together = (("climate_zone", "moisture_zone"))
        verbose_name = "Climate"
        verbose_name_plural = "Climate"

class Aboveground_Biomass(models.Model):
    value = models.FloatField()
    managed = models.BooleanField()
    name = models.CharField(max_length=80)
    continent = models.ForeignKey(Continent)
    biome = models.ForeignKey(Biome)
    units = models.CharField(max_length=80)
    def __unicode__(self):
        return str(self.id)
    class Meta:
        unique_together = ("managed", "continent", "biome")
        verbose_name = "AbovegroundBiomass"
        verbose_name_plural = "AbovegroundBiomass"

class Necromass(models.Model):
    litterC = models.FloatField(null=True)
    deadwoodC = models.FloatField(null=True)
    climate = models.ForeignKey(Climate, unique=True)
    units = models.CharField(max_length=80)
    def __unicode__(self):
        return self.climate.name
    class Meta:
        verbose_name = "Necromass"
        verbose_name_plural = "Necromass"

class Belowground_Ratio(models.Model):
    biome = models.ForeignKey(Biome)
    category = models.CharField(max_length=80)
    value = models.FloatField()
    def __unicode__(self):
        return str(self.id)
    class Meta:
        unique_together = ("biome", "category")
        verbose_name = "BelowgroundRatio"
        verbose_name_plural = "BelowgroundRatio"    

class Combustion_Factor(models.Model):
    biome = models.ForeignKey(Biome)
    pctReleased = models.FloatField()
    emissCO2 = models.FloatField()
    emissCH4 = models.FloatField()
    emissN2O = models.FloatField()
    def __unicode__(self):
        return str(self.id)
    class Meta:
        verbose_name = "CombustionFactor"
        verbose_name_plural = "CombustionFactor"    

class Land_Use(models.Model):
    name = models.CharField(max_length=80, unique=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "LandUse"
        verbose_name_plural = "LandUse"    

class Combustion_Land_Use(models.Model):
    land_use = models.ForeignKey(Land_Use)
    pctReleased = models.FloatField()
    emissCO2 = models.FloatField()
    emissCH4 = models.FloatField()
    emissN2O = models.FloatField()
    def __unicode__(self):
        return str(self.id)
    class Meta:
        verbose_name = "CombustionLandUse"
        verbose_name_plural = "CombustionLandUse"    

class Biomass_Land_Use(models.Model):
    land_use = models.ForeignKey(Land_Use)
    climate = models.ForeignKey(Climate)
    value = models.FloatField()
    previousOrFinal = models.CharField(max_length=1, choices=(("P", "Previous"), ("F", "Final")), default="P")
    age = models.FloatField(null=True)
    def __unicode__(self):
        return self.land_use.name
    class Meta:
        unique_together = ("land_use", "climate", "previousOrFinal")
        verbose_name = "BiomassLandUse"
        verbose_name_plural = "BiomassLandUse"    

class Soil_Carbon_Factor(models.Model):
    land_use = models.ForeignKey(Land_Use)
    climate = models.ForeignKey(Climate)
    value = models.FloatField()
    def __unicode__(self):
        return self.land_use.name
    class Meta:
        unique_together = ("land_use", "climate")
        verbose_name = "SoilCarbonFactor"
        verbose_name_plural = "SoilCarbonFactor"

class Soil_Carbon_Ref(models.Model):
    soil_type = models.ForeignKey(Soil_Type)
    climate = models.ForeignKey(Climate)
    value = models.FloatField(null=True)
    def __unicode__(self):
        return self.soil_type.name
    class Meta:
        unique_together = ("soil_type", "climate")
        verbose_name = "SoilCarbonRef"
        verbose_name_plural = "SoilCarbonRef"

class Agricultural_Practice(models.Model):
    name = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "AgriculturalPractice"
        verbose_name_plural = "AgriculturalPractice"

class Agriculture_Carbon_Stored(models.Model):
    agricultural_practice = models.ForeignKey(Agricultural_Practice)
    simple_climate = models.ForeignKey(Simple_Climate)
    amountC = models.FloatField()
    def __unicode__(self):
        return self.name
    class Meta:
        unique_together = ("agricultural_practice", "simple_climate")
        verbose_name = "AgricultureCarbonStored"
        verbose_name_plural = "AgricultureCarbonStored"
        
class Forest_Growth(models.Model):
    name = models.CharField(max_length=80)
    value = models.FloatField(help_text="Forest Aboveground Biomass Growth (t DM Ha-1 yr-1)")
    managed = models.BooleanField()
    continent = models.ForeignKey(Continent)
    biome = models.ForeignKey(Biome)
    youngOrOld = models.CharField(max_length=1, choices=(("Y", "Young"), ("O", "Old")))
    def __unicode__(self):
        return str(self.id)
    class Meta:
        unique_together = ("managed", "continent", "biome", "youngOrOld")
        verbose_name = "Forest_Growth"
        verbose_name_plural = "Forest_Growth"

class Rice_Practice(models.Model):
    # used for rice practices
    name = models.CharField(max_length=80)
    type = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "RicePractice"
        verbose_name_plural = "RicePractice"

class Rice_Emission(models.Model):
    value = models.FloatField()
    rice_practice = models.ForeignKey(Rice_Practice)
    def __unicode__(self):
        return repr((self.value, self.rice_practice.name))
    class Meta:
        verbose_name = "RiceEmission"
        verbose_name_plural = "RiceEmission"

class Grassland_Soil(models.Model):
    value = models.FloatField(help_text="Grassland Soil Carbon Scaling Factors")
    climate = models.ForeignKey(Climate)
    STATUS_CHOICES=(("B", "Base"), ("N", "non degraded"), ("M", "Moderately degraded"), ("I", "Improved medium"))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    def __unicode__(self):
        return repr((self.value, self.climate.name, self.status))
    class Meta:
        unique_together = ("status", "climate")
        verbose_name = "GrasslandSoil"
        verbose_name_plural = "GrasslandSoil"
        
class Grassland_Biomass(models.Model):
    value = models.FloatField(help_text="Default Grassland Biomass Stock (t DM Ha-1)")
    climate = models.ForeignKey(Climate)
    def __unicode__(self):
        return repr((self.value, self.climate.name))
    class Meta:
        verbose_name = "GrasslandBiomass"
        verbose_name_plural = "GrasslandBiomass"

