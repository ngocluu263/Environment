
"""
def generate_default_land_covers(proj_id):
    project = Project.objects.get(id=proj_id)
    climate = project.Climate()
    currentLandcovers = LandCover.objects.filter(project=project)
    currentPractices = Practice.objects.filter(project=project)

    if currentLandcovers is not None:
        currentLandcovers.delete()
    if currentPractices is not None:
        currentPractices.delete()
    
    necromass = Necromass.objects.get(climate=climate)

    if project.soil_type != None:
        soil_carbon = Soil_Carbon_Ref.objects.get(soil_type=project.soil_type, climate=climate)
    else:
        soil_carbon = Soil_Carbon_Ref.objects.get(soil_type=1, climate=climate)   

    biomes = Biome.objects.filter(climate_zone=project.climate_zone)
    land_use = Land_Use.objects.get(name='Forest')

    # Load forests
    for i, biome in enumerate(biomes):
        belowgroundRatios = Belowground_Ratio.objects.filter(biome=biome)
        combustionFactor = Combustion_Factor.objects.get(biome=biome)
        for managed in (False, True):
            aboveground_biomass = Aboveground_Biomass.objects.get(continent=project.continent, managed=managed, biome=biome)
            # to get belowground multiply aboveground by belowground ratio
            for belowgroundRatio in belowgroundRatios:
                category = belowgroundRatio.category
                abovegroundLimit = float(category[1:])
                if aboveground_biomass.value < abovegroundLimit: break
                belowgroundRatio_value = belowgroundRatio.value
            old_growth_rate = Forest_Growth.objects.get(managed=managed,continent=project.continent,
                biome=biome,youngOrOld='O')
            young_growth_rate = Forest_Growth.objects.get(managed=managed,continent=project.continent,
                biome=biome,youngOrOld='Y')
            name = project.continent.name+" "+biome.name
            if managed: name = name+" (plantation)"            
            soil_carbon_factor = Soil_Carbon_Factor.objects.get(land_use=land_use,climate=climate)
            LandCover(name=name, project = project,category='F',
                biomassa = aboveground_biomass.value, biomassb = aboveground_biomass.value*belowgroundRatio_value,
                litter = necromass.litterC, dead_wood = necromass.deadwoodC, soil = soil_carbon.value * soil_carbon_factor.value,
                combustion_pctreleased = combustionFactor.pctReleased,
                CH4 = combustionFactor.emissCH4, N2O = combustionFactor.emissN2O,
                old_growth_rate = old_growth_rate.value, young_growth_rate = young_growth_rate.value,
                biomassratio = belowgroundRatio_value).save()
    # Load one of each other type
    nfactor = 2.0 * project.cdm
    
    #Annual Crop
    land_use = Land_Use.objects.get(name='Annual Crop')
    soil_carbon_factor = Soil_Carbon_Factor.objects.get(land_use=land_use,climate=climate)
    biomass = Biomass_Land_Use.objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
    CF = Combustion_Land_Use.objects.get(land_use=land_use)
    LandCover(name=land_use.name, project=project, category='A',
              biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
              combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

    #Perennial/Tree Crop
    land_use = Land_Use.objects.get(name='Perennial/Tree Crop')
    CF = (Combustion_Land_Use.objects.filter(land_use=land_use))[0]
    soil_carbon_factor = Soil_Carbon_Factor.objects.get(land_use=land_use,climate=climate)
    biomass = Biomass_Land_Use.objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
    LandCover(name=land_use.name, project=project, category='P',
              biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
              combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

    #Paddy Rice
    land_use = Land_Use.objects.get(name='Paddy Rice')
    soil_carbon_factor = Soil_Carbon_Factor.objects.get(land_use=land_use,climate=climate)
    biomass = Biomass_Land_Use.objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
    CF = Combustion_Land_Use.objects.get(land_use=land_use)
    LandCover(name=land_use.name, project=project, category='R',
              biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
              combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()
    
    #Grassland
    land_use = Land_Use.objects.get(name='Grassland')
    soil_carbon_factor = Soil_Carbon_Factor.objects.get(land_use=land_use,climate=climate)
    biomass = Biomass_Land_Use.objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
    CF = Combustion_Land_Use.objects.get(land_use=land_use)
    LandCover(name=land_use.name, project=project, category='G',
              biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
              combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()      

    Practice(project=project,name='Default Practices').save()



   
def generate_default_land_covers(project):
    climate = project.Climate()
    currentLandcovers = get_model('ecalc', 'LandCover').objects.filter(project=project)
    currentPractices = get_model('ecalc', 'Practice').objects.filter(project=project)
    if currentLandcovers is not None:
        currentLandcovers.delete()
    if currentPractices is not None:
        currentPractices.delete()

    necromass = get_model('ecalc', 'Necromass').objects.get(climate=climate)
    if project.soil_type != None:
        soil_carbon = get_model('ecalc', 'Soil_Carbon_Ref').objects.get(soil_type=project.soil_type, climate=climate)
    else:
        soil_carbon = get_model('ecalc', 'Soil_Carbon_Ref').objects.get(soil_type=1, climate=climate)   
    biomes = get_model('ecalc', 'Biome').objects.filter(climate_zone=project.climate_zone)
    land_use = get_model('ecalc', 'Land_Use').objects.get(name='Forest')
    # Load forests
    for i, biome in enumerate(biomes):
        belowgroundRatios = get_model('ecalc', 'Belowground_Ratio').objects.filter(biome=biome)
        combustionFactor = get_model('ecalc', 'Combustion_Factor').objects.get(biome=biome)
        for managed in (False, True):
            aboveground_biomass = get_model('ecalc', 'Aboveground_Biomass').objects.get(continent=project.continent, managed=managed, biome=biome)
            # to get belowground multiply aboveground by belowground ratio
            for belowgroundRatio in belowgroundRatios:
                category = belowgroundRatio.category
                abovegroundLimit = float(category[1:])
                if aboveground_biomass.value < abovegroundLimit: break
                belowgroundRatio_value = belowgroundRatio.value
            old_growth_rate = get_model('ecalc', 'Forest_Growth').objects.get(managed=managed,continent=project.continent,biome=biome,youngOrOld='O')
            young_growth_rate = get_model('ecalc', 'Forest_Growth').objects.get(managed=managed,continent=project.continent,biome=biome,youngOrOld='Y')
            name = project.continent.name+" "+biome.name
            if managed: name = name+" (plantation)"            
            soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
            get_model('ecalc', 'LandCover')(name=name, project = project,category='F',
                biomassa = aboveground_biomass.value, biomassb = aboveground_biomass.value*belowgroundRatio_value,
                litter = necromass.litterC, dead_wood = necromass.deadwoodC, soil = soil_carbon.value * soil_carbon_factor.value,
                combustion_pctreleased = combustionFactor.pctReleased,
                CH4 = combustionFactor.emissCH4, N2O = combustionFactor.emissN2O,
                old_growth_rate = old_growth_rate.value, young_growth_rate = young_growth_rate.value,
                biomassratio = belowgroundRatio_value).save()
    # Load one of each other type
    nfactor = 2.0 * project.cdm

    land_use = get_model('ecalc', 'Land_Use').objects.get(name='Annual Crop')
    soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
    biomass = get_model('ecalc', 'Biomass_Land_Use').objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
    CF = get_model('ecalc', 'Combustion_Land_Use').objects.get(land_use=land_use)
    get_model('ecalc', 'LandCover')(name=land_use.name, project=project, category='A',
              biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
              combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

    land_use = get_model('ecalc', 'Land_Use').objects.get(name='Perennial/Tree Crop')
    CF = (get_model('ecalc', 'Combustion_Land_Use').objects.filter(land_use=land_use))[0]
    soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
    biomass = get_model('ecalc', 'Biomass_Land_Use').objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
    get_model('ecalc', 'LandCover')(name=land_use.name, project=project, category='P',
              biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
              combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

    land_use = get_model('ecalc', 'Land_Use').objects.get(name='Paddy Rice')
    soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
    biomass = get_model('ecalc', 'Biomass_Land_Use').objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
    CF = get_model('ecalc', 'Combustion_Land_Use').objects.get(land_use=land_use)
    get_model('ecalc', 'LandCover')(name=land_use.name, project=project, category='R',
              biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
              combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()

    land_use = get_model('ecalc', 'Land_Use').objects.get(name='Grassland')
    soil_carbon_factor = get_model('ecalc', 'Soil_Carbon_Factor').objects.get(land_use=land_use,climate=climate)
    biomass = get_model('ecalc', 'Biomass_Land_Use').objects.get(land_use=land_use,climate=climate,previousOrFinal='P')
    CF = get_model('ecalc', 'Combustion_Land_Use').objects.get(land_use=land_use)
    get_model('ecalc', 'LandCover')(name=land_use.name, project=project, category='G',
              biomassa = biomass.value/nfactor, biomassb = biomass.value/nfactor, soil=soil_carbon.value * soil_carbon_factor.value,
              combustion_pctreleased = CF.pctReleased, CH4 = CF.emissCH4, N2O = CF.emissN2O, biomassratio = 0.5).save()      

    get_model('ecalc', 'Practice')(project=project,name='Default Practices').save()
    """