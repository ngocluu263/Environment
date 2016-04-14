from django.conf import settings
from models import CarbonPools
from copy import deepcopy

def UpdatePools(scenario):
    # remove previous pools for this parcel
    CarbonPools.objects.filter(scenario=scenario).delete()
    # First year pool and initial values
    last_pool = scenario.InitialPools()
    last_pool.save()
    last_emissions = 0
    last_nonco2 = 0
    dur = scenario.project.duration
    for i in range(0,scenario.project.duration+1):
        # copy last_pool
        pool = deepcopy(last_pool)
        pool.id = None
        pool.year = i

        #Calls ecalc models.py --> Class Scenario --> def LandCover
        pool.landcover = scenario.LandCover(i)
        
        if last_pool.landcover == pool.landcover:
            # Update
            if i != 0:
                # Update
                pool.Age()
                pool.Grow()
                pool.Practice()
                #pool.save()
        if i != 0:
            nonco2 = pool.GetNonCO2
            pool.annual_nonco2 = nonco2 - last_nonco2
            last_nonco2 = nonco2
            pool.annual_emissions = pool.GetAtm - nonco2 - last_emissions
            last_emissions = pool.GetAtm - nonco2
            pool.save()
        # Conversion - occurs after save
        # treating all cases as conversions
        #if last_pool.landcover != pool.landcover or last_pool.GetLandUse.degraded != pool.GetLandUse.degraded:
        if i == 0 or last_pool.landcover != pool.landcover or last_pool.GetLandUse != pool.GetLandUse:
            if last_pool.GetLandCat == 'F':
                # harvest wood
                pool.Harvest(pool.GetLandUse.prior_harvest)
            # burn
            pool.Burn(last_pool.landcover.combustion_pctreleased, last_pool.landcover.CH4, last_pool.landcover.N2O)
            # decompose remaining biomass, deadwood, litter (move to atmosphere)
            pool.Decompose()
            # Reset pools to new converted land values
            pool.Convert()
            if last_pool.GetLandCat != 'F' and pool.GetLandCat == 'F':
                # reset biomass to 0
                pool.atm_carbon += (pool.biomassa + pool.biomassb)
                pool.biomassa = 0.0
                pool.biomassb = 0.0
        last_pool = pool
        
        
from ipcc import *

FILENAME = "./EX-ACT_version_3.1.2_-_Fev_2011_-_EN.xls"
SHEETNAMES = {'climate':'Climate', 'list': 'List', 'ipcc':' IPCC', 'elec':'Elec EF'}

def delete_ipcc():
    ipcc_tables = ('GWP', 'Moisture_Zone', 'Continent', 'Climate_Zone', 'Biome', 'Simple_Climate', 'Climate', 'Grassland_Soil',
                   'Grassland_Biomass', 'Rice_Practice', 'Rice_Emission', 'Aboveground_Biomass', 'Necromass', 'Belowground_Ratio',
                   'Combustion_Factor', 'Land_Use', 'Combustion_Land_Use', 'Biomass_Land_Use', 'Soil_Carbon_Factor', 'Soil_Type',
                   'Soil_Carbon_Ref', 'Agricultural_Practice', 'Agriculture_Carbon_Stored', 'Forest_Growth')
    for name in ipcc_tables:
        try:
            thing = eval(name)            
            
            objs = thing.objects.all()            
            if objs.count > 0:
                objs.delete()
        except:
            pass

def load_ipcc():
    # clear out old data if any

    # extract all the data from the worksheets
    #print "reading IPCC"
    data = xls_read_data(FILENAME, SHEETNAMES['ipcc'])
    #print "reading Climate"
    data_climate = xls_read_data(FILENAME, SHEETNAMES['climate'])

    # GWP
    #print "GWP"

    if not GWP.objects.count():
        gwp_names = ('Official CDM', 'Last Update (IPCC-2007)',)
        for gwp_name in gwp_names:
            c = GWP(name=gwp_name)
            c.save()

    # Moisture Zone    
    #print "Moisture Zone"
    if not Moisture_Zone.objects.count():
        moistureZone_names = ('Dry', 'Moist', 'Wet',)
        for moistureZone_name in moistureZone_names:        
            c = Moisture_Zone(name=moistureZone_name)
            c.save()

    # Continent
    #print "Continent"
    if not Continent.objects.count():
        for i in range(11):
            irow = i + 11
            continent_name = data[irow][0]
            c = Continent(name=continent_name)
            c.save()

    # ClimateZone
    #print "Climate Zone"
    if not Climate_Zone.objects.count():
        for i in range(5):
            icol = i + 1
            value = data[2][icol]
            if value != '':
                climatezone_name = value
                c = Climate_Zone(name=climatezone_name)
                c.save()

    # ClimateZone
    #print "Climate Zone"
    if not Biome.objects.count():
        for i in range(5):
            icol = i + 1
            value = data[2][icol]
            if value != '':
                climatezone_name = value
                c = Climate_Zone.objects.get(name=climatezone_name)
                for j in range(4):
                    jrow = j + 3
                    value = data[jrow][icol]
                    if value == '': continue
                    biome_name = value
                    b = Biome(name=biome_name)
                    b.climate_zone = c
                    b.save()

    # Simple Climate
    #print "Simple Climate"
    if not Simple_Climate.objects.count():
        startrow = 593
        for j in range(4):
            jcol = j + 1
            simpleClimate_name = data[startrow][jcol]
            s = Simple_Climate()
            s.name = simpleClimate_name
            s.save()
        
    # Climate
    #print "Climate"
    if not Climate.objects.count():
        for i in range(11):
            irow = i + 70
            climate_name = data[irow][0]
            climateZone_name, moistureZone_name = climate_name.rsplit(' ', 1)
            c = Climate(name=climate_name)
            c.climate_zone = Climate_Zone.objects.get(name=climateZone_name)
            c.moisture_zone = Moisture_Zone.objects.get(name=moistureZone_name)
            c.save()
        startrow = 34
        for i in range(11):
            irow = startrow + i
            climate_name = data_climate[irow][11]
            simpleClimate_name = data_climate[irow][12]
            c = Climate.objects.get(name=climate_name)
            c.simple_climate = Simple_Climate.objects.get(name=simpleClimate_name)
            c.save()

    # Grassland Soil
    #print "Grassland Soil"
    if not Grassland_Soil.objects.count():
        startrow = 627
        for i in range(11):
            irow = startrow + i + 2
            climate_name = data[irow][0]
            climate = Climate.objects.get(name=climate_name)
            for j in range(4):
                icol = j + 1
                status_name = data[startrow][icol]
                c = Grassland_Soil()
                c.value = float(data[irow][icol])
                c.status = status_name[0].upper()
                c.climate = climate
                c.save()
            
    # Grassland Biomass
    #print "Grassland Biomass"
    if not Grassland_Biomass.objects.count():
        startrow = 642
        for i in range(11):
            irow = startrow + i + 2
            climate_name = data[irow][0]
            c = Grassland_Biomass()
            c.climate = Climate.objects.get(name=climate_name)
            c.value = float(data[irow][1])
            c.save()

    # Rice Practice
    #print "Rice Practice"
    if not Rice_Practice.objects.count():
        startrow = 602
        practice_type = data[startrow][0]+" (during)"
        for i in range(3):
            irow = i + 2 + startrow
            practice_name = data[irow][0]
            c = Rice_Practice()
            c.type = practice_type
            c.name = practice_name
            c.save()
        startrow = 609
        practice_type = data[startrow][0]+" (before)"
        for i in range(3):
            irow = i + 2 + startrow
            practice_name = data[irow][0]
            c = Rice_Practice()
            c.type = practice_type
            c.name = practice_name
            c.save()    
        startrow = 616
        practice_type = data[startrow][0]
        for i in range(7):
            irow = i + 2 + startrow
            practice_name = data[irow][0]
            c = Rice_Practice()
            c.type = practice_type
            c.name = practice_name
            c.save()
    
    # Rice Emission
    #print "Rice Emission"
    if not Rice_Emission.objects.count():
        startrow = 602
        for i in range(3):
            irow = i + 2 + startrow
            practice_name = data[irow][0]
            value = data[irow][1]
            c = Rice_Emission()
            c.value = float(value)
            c.rice_practice = Rice_Practice.objects.get(name=practice_name)
            c.save()
        startrow = 609
        for i in range(3):
            irow = i + 2 + startrow
            practice_name = data[irow][0]
            value = data[irow][1]
            c = Rice_Emission()
            c.value = float(value)
            c.rice_practice = Rice_Practice.objects.get(name=practice_name)
            c.save()
        startrow = 616
        for i in range(7):
            irow = i + 2 + startrow
            practice_name = data[irow][0]
            value = data[irow][1]
            c = Rice_Emission()
            c.value = float(value)
            c.rice_practice = Rice_Practice.objects.get(name=practice_name)
            c.save()

    # AbovegroundBiomass
    #print "Aboveground Biomass"
    if not Aboveground_Biomass.objects.count():
        startpoints = ((9,0), (9,7), (24,0), (24,7), (39,0), (39,7), (54,0), (54,7),)
        for startpoint in startpoints:
            startrow, startcol = startpoint
            name = data[startrow][startcol]
            if name.startswith("FOREST"):
                managed = False
            elif name.startswith("PLANTATION"):
                managed = True
            else:
                raise Exception, "bad name"+name
            for i in range(11):
                irow = startrow + i + 2
                continent_name = data[irow][startcol]            
                for j in range(5):
                    jcol = startcol + j + 1
                    value = data[irow][jcol]
                    if value == '': continue
                    continent = Continent.objects.get(name=continent_name)
                    biome_name = data[startrow][jcol]                
                    biome = Biome.objects.get(name=biome_name)
                    biomass = Aboveground_Biomass(name=name, value=value)
                    biomass.continent = continent
                    biomass.biome = biome
                    biomass.managed = managed
                    biomass.save()
    
    # Necromass
    #print "Necromass"
    if not Necromass.objects.count():
        for i in range(11):
            irow = i + 70
            climate_name = data[irow][0]
            litterC = data[irow][1]
            deadwoodC = data[irow][2]
            c = Necromass()
            climate = Climate.objects.get(name=climate_name)
            c.climate = climate
            if litterC != '':
                c.litterC = float(litterC)
            else:
                c.litterC = 0.0
            if deadwoodC != '':
                c.deadwoodC = float(deadwoodC)
            else:
                c.deadwoodC = 0.0
            c.save()

    # Belowground Ratio
    #print "Belowground Ratio"
    if not Belowground_Ratio.objects.count():
        startrow = 83
        for i in range(15):
            irow = startrow + i + 1
            biome_name = data[irow][0]
            for j in range(5):
                icol = j + 1
                c = Belowground_Ratio()
                biome = Biome.objects.get(name=biome_name)
                category = data[startrow][icol]
                value = data[irow][icol]
                c.biome = biome
                c.category = category
                c.value = float(value)
                c.save()

    # Combustion Factor
    #print "Combustion Factor"
    if not Combustion_Factor.objects.count():
        startrow = 101
        for i in range(15):
            irow = startrow + i + 2
            biome_name = data[irow][0]
            c = Combustion_Factor()
            c.biome = Biome.objects.get(name=biome_name)
            # proportion of pre-fire fuel biomass burned
            c.pctReleased = float(data[irow][1])
            # g GHG per kg dry matter burned
            c.emissCO2 = float(data[irow][2])
            c.emissCH4 = float(data[irow][3])
            c.emissN2O = float(data[irow][4])
            c.save()

    # Land Use
    #print "Land Use"
    if not Land_Use.objects.count():
        startrow = 150
        for j in range(8):
            jcol = j + 1
            landUse_name = data[startrow][jcol]
            c = Land_Use(name=landUse_name)
            c.save()
        # add forest
        c = Land_Use(name="Forest")
        c.save()
    
    # Combustion Land Use
    #print "Combustion Land Use"
    if not Combustion_Land_Use.objects.count():
        startrow = 316
        for i in range(9):
            irow = startrow + i + 1
            land_use_name = data[irow][0]
            # perennial/tree crops are all the same
            land_use_name = land_use_name.split('(')[0].strip()
            try:
                #print land_use_name
                c = Combustion_Land_Use()
                c.land_use = Land_Use.objects.get(name=land_use_name)
                # proportion of pre-fire fuel biomass burned
                c.pctReleased = float(data[irow][1])
                # g GHG per kg dry matter burned
                c.emissCO2 = float(data[irow][2])
                c.emissCH4 = float(data[irow][3])
                c.emissN2O = float(data[irow][4])
                c.save()
            except:
                pass

    # Biomass Land Use
    #print "Biomass Land Use"
    if not Biomass_Land_Use.objects.count():
        startrow = 120
        for j in range(8):
            jcol = j + 1
            landUse_name = data[startrow][jcol]        
            for i in range(11):
                irow = i + startrow + 2
                climate_name = data[irow][0]
                climate = Climate.objects.get(name=climate_name)
                landUse = Land_Use.objects.get(name=landUse_name)
                value = float(data[irow][icol])
                c = Biomass_Land_Use(value=value)
                c.climate = climate
                c.land_use = landUse
                c.save()

    # Soil Carbon Factor
    #print "Soil Carbon Factor"
    if not Soil_Carbon_Factor.objects.count():
        startrow = 150
        for i in range(11):
            irow = i + startrow + 2
            climate_name = data[irow][0]
            climate = Climate.objects.get(name=climate_name)
            for j in range(8):
                jcol = j + 1
                landUse_name = data[startrow][jcol]        
                landUse = Land_Use.objects.get(name=landUse_name)
                value = float(data[irow][jcol])
                c = Soil_Carbon_Factor(value=value)
                c.climate = climate
                c.land_use = landUse
                c.save()
            # add forest
            landUse_name = "Forest"
            landUse = Land_Use.objects.get(name=landUse_name)
            c = Soil_Carbon_Factor(value=1.0)
            c.climate = climate
            c.land_use = landUse
            c.save()

    # Soil Type
    #print "Soil Type"
    if not Soil_Type.objects.count():
        for i in range(7):
            icol = i + 2
            soilType_name = data[564][icol].split()[0]
            c = Soil_Type(name=soilType_name)
            c.save()

    # Soil Carbon Reference
    #print "Soil Carbon Reference"
    if not Soil_Carbon_Ref.objects.count():
        startrow = 564
        for j in range(7):
            jcol = j + 2
            soilType_name = data[startrow][jcol].split()[0]
            for i in range(11):
                irow = startrow + i + 2
                climate_name = data[irow][0]
                climate = Climate.objects.get(name=climate_name)
                soilType = Soil_Type.objects.get(name=soilType_name)
                value = data[irow][jcol]
                c = Soil_Carbon_Ref()
                if value != '':
                    c.value = float(value)
                else:
                    c.value = 0.0
                c.climate = climate
                c.soil_type = soilType
                c.save()

    # Agricultural Practice
    #print "Agricultural Practice"
    if not Agricultural_Practice.objects.count():
        startrow = 593
        for i in range(6):
            irow = startrow + i + 1
            agriculturalPractice_name = data[irow][0]
            a = Agricultural_Practice(name=agriculturalPractice_name)
            a.save()

    # Agriculture Carbon Stored
    #print "Agriculture Carbon Stored"
    if not Agriculture_Carbon_Stored.objects.count():
        startrow = 593
        for i in range(6):
            irow = startrow + i + 1
            agriculturalPractice_name = data[irow][0]
            for j in range(4):
                jcol = j + 1
                simpleClimate_name = data[startrow][jcol]
                amountC = data[irow][jcol]
                c = Agriculture_Carbon_Stored()
                c.simple_climate = Simple_Climate.objects.get(name=simpleClimate_name)
                c.agricultural_practice = Agricultural_Practice.objects.get(name=agriculturalPractice_name)
                c.amountC = amountC
                c.save()

    # Forest Growth
    #print "Forest Growth"
    if not Forest_Growth.objects.count():
        startpoints = ((165,0), (165,7), (180,0), (180,7), (195,0), (195,7), (210,0), (210,7),
                       (225,0), (225,7), (240,0), (240,7), (255,0), (255,7), (270,0), (270,7))
        for startpoint in startpoints:
            startrow, startcol = startpoint
            name = data[startrow][startcol]
            if name.startswith("FOREST"):
                managed = False
            elif name.startswith("PLANTATION"):
                managed = True
            else:
                raise Exception, "bad name"+name
            if startrow > 210:
                youngOrOld = "O"
            else:
                youngOrOld = "Y"
            for i in range(11):
                irow = startrow + i + 2
                continent_name = data[irow][startcol]
                for j in range(5):
                    jcol = startcol + j + 1
                    value = data[irow][jcol]
                    if value == '': continue
                    continent = Continent.objects.get(name=continent_name)
                    biome_name = data[startrow][jcol]                
                    biome = Biome.objects.get(name=biome_name)
                    growth = Forest_Growth(name=name, value=float(value))
                    growth.continent = continent
                    growth.biome = biome
                    growth.managed = managed
                    growth.youngOrOld = youngOrOld
                    growth.save()

def load_elec():
    pass

def load_list():
    pass

def xls_read_data(filename, sheetname):
    """ get the data from the spreadsheet as a list dictionary records """
    import xlrd
    import datetime
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_name(sheetname)
    data = []
    nrows = sh.nrows
    for rownum in range(nrows):
        row = sh.row_values(rownum)
        cells = []
        for colnum,col in enumerate(row):
            cells.append(col)
        data.append(cells)
    return data

def extract_fields(data, rowstart=None, colstart=None, rowend=None, colend=None):
    if not rowend: rowend = rowstart    
    if not colend: colend = colstart
    ncol = len(data[0])
    colnames = xls_map_columnnames(ncol)
    colstart = colnames[colstart]
    colend = colnames[colend]
    result = []
    for irow in range(rowstart-1, rowend):
        for icol in range(colstart, colend+1):
            value = data[irow][icol]
            try:
                if value != '':
                    result.append(value)
            except:
                pass
            # end try
        # end for
    return result

def xls_map_columnnames(ncols=100):
    """ convert column number to index starting from 0 """
    results = {}
    for icol in range(ncols):
        index = icol + 1
        result = ""
        while True:
            if index > 26:
                index, remainder = divmod(index - 1, 26)
                result = chr(remainder + ord('A')) + result
            else:
                result = str(chr(index + ord('A') - 1) + result)
                results[result] = icol
                break
            # end if
        # end while
    return results        