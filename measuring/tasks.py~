from __future__ import absolute_import
#from celery import Celery
from celery import shared_task
from django.http import HttpResponse
import allometric
#from mrvapi.models import Project, Parcel, Plot, Tree
from mrvapi.models import *
import numpy
import scipy
#from decimal import Decimal
#from .models import TreeAEQ
from decimal import *
from .models import *

#app = Celery('tasks', broker='amqp://gchange:cgv4tr9v4xl5@35.8.163.102:5672/nevis')

DEFAULT_REGION_EQUATIONS = {
    'Central Highlands' : '7.420770 (dbh/100)^2 - 0.838878 (dbh/100) + 0.023708',
    'North-Eastern Ranges' : '0.15958 - 1.57976 (dbh/100) + 8.25014 (dbh/100)^2 - 0.48518 (dbh/100)^3',
    'East Coast' : '8.760534 (dbh/100)^2 - 1.449236 (dbh/100) + 0.088074',
    'Western Plain' : '0.081467 - 1.063661 (dbh/100) + 6.452918 (dbh/100)^2',
    'East Deccan' : '8.760534 (dbh/100)^2 - 1.449236 (dbh/100) + 0.088074',
    'South Deccan' : '0.088183 - 1.490948 (dbh/100) + 8.984266 (dbh/100)^2'
}

@shared_task
def add(x, y):
    return x + y

@shared_task
def calculateTotalCarbonStocks(project_id):
    print "here"
    '''
        This process will handle the calculations for an entire project.

        Calculating the carbon stocks for each parcel will be done on separate
        processes/threads as they can be done simulaneously.

        Calculating the carbon stocks for the project can only be done
        after each parcel has been calculated.
    '''

    project_carbon_stock = Project.objects.get(id=project_id)

    for parcel in project_carbon_stock.parcel_set.all():
        #----------------------------------------------
        #parcelCalculate(parcel.id)
        #----------------------------------------------
        TreeAEQ.objects.filter(parcel=parcel).delete()
        p = parcelCalculate(parcel.id)
        project_carbon_stock.agb_tc      += Decimal(str(p.agb_tc)[:14])
        project_carbon_stock.bgb_tc      += Decimal(str(p.bgb_tc)[:14])
        project_carbon_stock.soc_tc      += Decimal(str(p.soc_tc)[:14])
        project_carbon_stock.deadwood_tc += Decimal(str(p.deadwood_tc)[:14])
        project_carbon_stock.litter_tc 	 += Decimal(str(p.litter_tc)[:14])
    
    b= project_carbon_stock._get_project_carbon_stocks()
    project_carbon_stock.total_tc = b.total_tc
    #print "All parcels calculated"
    project_carbon_stock.save()
    #print "Project saved"
    return True

def parcelCalculate(parcel_id):
    print " in here"
    '''
        The purpose of this method is to do the carbon stock calculations for an individual parcel.
    '''
    def calculateParcelStatistics(biomass_list_data):
        '''
            This function will be used to calculate the statistics for the
            variance forms of biomass for parcels. It calculates the mean
            standard deviation, variance, t-statistic, and control chart
        '''

        if len(biomass_list_data) < 1:
            return (0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0)

        mean        = 0.0
        variance    = 0.0
        std         = 0.0
        t_statistic = 0.0
        n_plots     = 0
        min_95      = 0.0
        max_95      = 0.0
        perc_95     = 0.0

        mean     = numpy.mean(biomass_list_data)
        variance = numpy.var(biomass_list_data, ddof=1, dtype=float)

        if numpy.isnan(variance):
            variance = 0.0

        std            = numpy.sqrt(variance)
        n_plots        = len(biomass_list_data)
        standard_error = t_statistic = std / numpy.sqrt(n_plots)
        t_statistic    = scipy.stats.t.isf(0.025, n_plots - 1)

        if numpy.isnan(t_statistic):
            t_statistic = 0.0

        min_95  = mean - t_statistic * standard_error
        max_95  = mean + t_statistic * standard_error
        perc_95 = (max_95 / mean - 1) * 100

        return (mean, variance, std, n_plots, min_95, max_95, perc_95)

    parcel = Parcel.objects.get(id=parcel_id)
    plot_count = 0

    agb        = []
    bgb        = []
    soc        = []
    litter     = []
    deadwood   = []
    agb_tdm    = []
    bgb_tdm    = []
    trees_list = []

    variance_total = 0.0

    for p in parcel.plot_set.all():
        carbon_values = plotCalculate(p.id)
        print carbon_values
        if carbon_values[0] is not None:
            agb.append(carbon_values[0])
        if carbon_values[1] is not None:
            bgb.append(carbon_values[1])
        if carbon_values[2] is not None:
            soc.append(carbon_values[2])
        if carbon_values[3] is not None:
            litter.append(carbon_values[3])
        if carbon_values[4] is not None:
            deadwood.append(carbon_values[4])
        if carbon_values[5] is not None:
            agb_tdm.append(carbon_values[5])
        if carbon_values[6] is not None:
            bgb_tdm.append(carbon_values[6])
        if carbon_values[7] is not None:
            trees_list.append(carbon_values[7])

    if any(agb):

        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(agb)

        parcel.mean_agb_tc_ha    = mean
        parcel.std_agb_tc_ha     = std
        parcel.n_plots_agb       = n_plots
        parcel.min_95_agb_tc_ha  = min_95
        parcel.max_95_agb_tc_ha  = max_95
        parcel.perc_95_agb_tc_ha = perc_95

        variance_total += variance


    if any(bgb):
        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(bgb)

        parcel.mean_bgb_tc_ha    = mean
        parcel.std_bgb_tc_ha     = std
        parcel.n_plots_bgb       = n_plots
        parcel.min_95_bgb_tc_ha  = min_95
        parcel.max_95_bgb_tc_ha  = max_95
        parcel.perc_95_bgb_tc_ha = perc_95

        variance_total += variance


    if any(soc):
        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(soc)

        parcel.mean_soc_tc_ha    = mean
        parcel.std_soc_tc_ha     = std
        parcel.n_plots_soc       = n_plots
        parcel.min_95_soc_tc_ha  = min_95
        parcel.max_95_soc_tc_ha  = max_95
        parcel.perc_95_soc_tc_ha = perc_95

        variance_total += variance

    if any(litter):
        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(litter)

        parcel.mean_litter_tc_ha    = mean
        parcel.std_litter_tc_ha     = std
        parcel.n_plots_litter       = n_plots
        parcel.min_95_litter_tc_ha  = min_95
        parcel.max_95_litter_tc_ha  = max_95
        parcel.perc_95_litter_tc_ha = perc_95

        variance_total += variance

    if any(deadwood):
        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(deadwood)

        parcel.mean_deadwood_tc_ha    = mean
        parcel.std_deadwood_tc_ha     = std
        parcel.n_plots_deadwood       = n_plots
        parcel.min_95_deadwood_tc_ha  = min_95
        parcel.max_95_deadwood_tc_ha  = max_95
        parcel.perc_95_deadwood_tc_ha = perc_95

        variance_total += variance

    if any(agb_tdm):
        parcel.mean_agb_tdm_ha = numpy.mean(agb_tdm)
        parcel.std_agb_tdm_ha  = numpy.std(agb_tdm, ddof=1, dtype=float)
        if numpy.isnan(parcel.std_agb_tdm_ha):
            parcel.std_agb_tdm_ha = 0.0
    if any(bgb_tdm):
        parcel.mean_bgb_tdm_ha = numpy.mean(bgb_tdm)
        parcel.std_bgb_tdm_ha  = numpy.std(bgb_tdm, ddof=1, dtype=float)
        if numpy.isnan(parcel.std_bgb_tdm_ha):
            parcel.std_bgb_tdm_ha = 0.0
    if any(trees_list):
        parcel.mean_trees_ha = numpy.mean(trees_list)
        parcel.std_trees_ha  = numpy.std(trees_list, ddof=1, dtype=float)
        if numpy.isnan(parcel.std_trees_ha):
            parcel.std_trees_ha = 0.0

    parcel.save()
    return parcel

def plotCalculate(plot_id):
    print " starting plot"
    def sumOfSquares(square, reg, mean, count):
        return square-(2*mean*reg)+(count*mean**2) if count else 0.0

    def extrapolate(value, area, subplot_area):
        return value * area / subplot_area if subplot_area else 0.0

    def calculate_tree_agb(tree, area, subplot_area):
        equations = None
        equationspecies = None
        species = tree.species
        genus = tree.genus

        if tree.plot.calculate_by_species:
            if genus and tree.plot.region:
                try:
                    equationspecies = allometric.models.EquationSpecies.objects.get(genus__iexact=genus, name__iexact=species)
                except Exception as e:
                    try:
                        equationspecies = allometric.models.EquationSpecies.objects.get(genus__iexact=genus, name='species')
                    except:
                        equationspecies=None

            try:
                if not tree.plot.region:
                    raise Exception('No region')
                equations = allometric.models.Equation.objects.filter(species=equationspecies.pk, region=tree.plot.region)
                if not equations:
                    equations = allometric.models.Equation.objects.filter(species=None, region=tree.plot.region)
                    #this is grabbing all the equations for a region.  don't we want it to grab the default equation for the region only?

                if not equations or len(equations) == 0:
                    if tree.plot.region.name in DEFAULT_REGION_EQUATIONS:
                       c = allometric.models.Equation()
                       c.string = DEFAULT_REGION_EQUATIONS[tree.plot.region.name]
                       equations = [c]
                if not equations:
                    raise Exception('No equation available')
            except:
                equations = [tree.plot.get_aeq()]
        else:
            equations = [tree.plot.get_aeq()]

        # if tree.plot.calculate_by_species:
        #     equations = tree.aeqs.all()
        #     print equations
        # else:
        #     equations = [tree.plot.get_aeq()]

        agb_kg_dm = 0.0
        equation_list_objects = list()
        for eq in equations:
            temp = eq._calculate_agb(tree)
            if eq.volumetric:
                #if tree.wood_gravity:
                #    temp = temp * tree.wood_gravity * 1000 #gives kg of biomass
            	#elif equationspecies.wood_gravity:
            	#	temp = temp * equationspecies.wood_gravity * 1000
                #else:
                if tree.wood_gravity:
                    temp = temp * tree.wood_gravity * 1000
                else:
                    temp = temp * 0.7 * 1000 #gives kg of biomass
            elif eq.less_than_ten:
                if not eq.is_less_than_dbh(tree.dbh):
                    temp = 0
            elif not eq.less_than_ten:
                if eq.is_less_than_dbh(tree.dbh) and eq.region:
                    temp = 0
            agb_kg_dm += temp
            if eq.id:
                c = TreeAEQ(tree=tree, aeq=eq, parcel=tree.plot.parcel, plot=tree.plot)
                equation_list_objects.append(c)

        TreeAEQ.objects.bulk_create(equation_list_objects)
        if agb_kg_dm == 0.0:
            tree.used_in_calculations = False
            tree.comments = "Tree not used in calculations"
            tree.save()
        return agb_kg_dm


    '''
        The purpose of this method is to do the carbon stock calculations for an individual plot.
    '''
    plot_carbon_stock = Plot.objects.get(id=plot_id)
    Trees = plot_carbon_stock.tree_set.all()

    subplots = [plot_carbon_stock.subplot_1_area, plot_carbon_stock.subplot_2_area, plot_carbon_stock.subplot_3_area, plot_carbon_stock.area]
    estimated_trees = 0.0
    trees_ha        = 0.0

    # These are the variables that we will use to store the
    # overall calculations
    dbh_mean          = 0.0
    height_mean       = 0.0
    wsg_mean          = 0.0

    dbh_sd            = 0.0
    height_sd         = 0.0
    wsg_sd            = 0.0

    dbh             = [ 0.0, 0.0, 0.0, 0.0 ]
    dbh_sq          = [ 0.0, 0.0, 0.0, 0.0 ]
    height          = [ 0.0, 0.0, 0.0, 0.0 ]
    height_sq       = [ 0.0, 0.0, 0.0, 0.0 ]
    wsg             = [ 0.0, 0.0, 0.0, 0.0 ]
    wsg_sq          = [ 0.0, 0.0, 0.0, 0.0 ]
    trees           = [ 0.0, 0.0, 0.0, 0.0 ]
    agb_kg_dm       = [ 0.0, 0.0, 0.0, 0.0 ]

    for t in Trees:
        if t.dbh is None:
            continue
        elif t.dbh > plot_carbon_stock.subplot_1_lower_bound and t.dbh <= plot_carbon_stock.subplot_1_upper_bound:
            print "elif 1"
            agb_kg_dm[0] += calculate_tree_agb(t, plot_carbon_stock.area, plot_carbon_stock.subplot_1_area)
            trees[0] += 1

            dbh[0]                += t.dbh
            dbh_sq[0]             += t.dbh**2

            height[0]             += t.total_height if t.total_height else 0.0
            height_sq[0]          += t.total_height**2 if t.total_height else 0.0

            wsg[0]                += t.wood_gravity if t.wood_gravity else 0.0
            wsg_sq[0]             += t.wood_gravity if t.wood_gravity else 0.0
        elif t.dbh > plot_carbon_stock.subplot_2_lower_bound and t.dbh <= plot_carbon_stock.subplot_2_upper_bound:
            print "elif 2"
            
            agb_kg_dm[1] += calculate_tree_agb(t, plot_carbon_stock.area, plot_carbon_stock.subplot_2_area)
            trees[1] += 1

            dbh[1]                += t.dbh
            dbh_sq[1]             += t.dbh**2

            height[1]             += t.total_height if t.total_height else 0.0
            height_sq[1]          += t.total_height**2 if t.total_height else 0.0

            wsg[1]                += t.wood_gravity if t.wood_gravity else 0.0
            wsg_sq[1]             += t.wood_gravity**2 if t.wood_gravity else 0.0
            
            
        elif t.dbh > plot_carbon_stock.subplot_3_lower_bound and t.dbh <= plot_carbon_stock.subplot_3_upper_bound:
            print "elif 3"
            agb_kg_dm[2] += calculate_tree_agb(t, plot_carbon_stock.area, plot_carbon_stock.subplot_3_area)
            trees[2] += 1

            dbh[2]                += t.dbh
            dbh_sq[2]             += t.dbh**2

            height[2]             += t.total_height if t.total_height else 0.0
            height_sq[2]          += t.total_height**2 if t.total_height else 0.0

            wsg[2]                += t.wood_gravity if t.wood_gravity else 0.0
            wsg_sq[2]             += t.wood_gravity**2 if t.wood_gravity else 0.0
        else:
            agb_kg_dm[3] += calculate_tree_agb(t, plot_carbon_stock.area, plot_carbon_stock.area)
            trees[3] += 1

            dbh[3]                += t.dbh
            dbh_sq[3]             += t.dbh**2

            height[3]             += t.total_height if t.total_height else 0.0
            height_sq[3]          += t.total_height**2 if t.total_height else 0.0

            wsg[3]                += t.wood_gravity if t.wood_gravity else 0.0
            wsg_sq[3]             += t.wood_gravity**2 if t.wood_gravity else 0.0

    #estimated_trees = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(trees, subplots)])
    estimated_trees = trees[0] + trees[1] + trees[2] + trees[3]
    if plot_carbon_stock.area is not None and plot_carbon_stock.area != 0.0:
        trees_ha = estimated_trees / plot_carbon_stock.area
    else:
        trees_ha = None

    height_mean = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(height, subplots)]) / estimated_trees if estimated_trees else 0.0
    dbh_mean    = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(dbh, subplots)]) / estimated_trees if estimated_trees else 0.0
    wsg_mean    = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(wsg, subplots)]) / estimated_trees if estimated_trees else 0.0

    dbh_sum_sq    = sum([extrapolate(sumOfSquares(x,y,dbh_mean,z),plot_carbon_stock.area,w) for w,x,y,z in zip(subplots, dbh_sq, dbh, trees)])
    height_sum_sq = sum([extrapolate(sumOfSquares(x,y,height_mean,z),plot_carbon_stock.area,w) for w,x,y,z in zip(subplots, height_sq, height, trees)])
    wsg_sum_sq    = sum([extrapolate(sumOfSquares(x,y,wsg_mean,z),plot_carbon_stock.area,w) for w,x,y,z in zip(subplots, wsg_sq, wsg, trees)])

    height_sd = numpy.sqrt(height_sum_sq / (estimated_trees - 1)) if estimated_trees and estimated_trees > 1 else 0.0
    dbh_sd    = numpy.sqrt(dbh_sum_sq / (estimated_trees - 1)) if estimated_trees and estimated_trees > 1 else 0.0
    wsg_sd    = numpy.sqrt(wsg_sum_sq / (estimated_trees - 1)) if estimated_trees and estimated_trees > 1 else 0.0

    sum_agb_kg_dm = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(agb_kg_dm, subplots)])

    agb_tdm_ha     = (sum_agb_kg_dm / 1000.0) / plot_carbon_stock.area if plot_carbon_stock.area else 0.0
    agb_tc_ha      = (sum_agb_kg_dm / 1000.0 * .47) / plot_carbon_stock.area if plot_carbon_stock.area else 0.0

    bgb_tdm_ha     = agb_tdm_ha * plot_carbon_stock.root_shoot_ratio if agb_tdm_ha is not None else 0.0
    bgb_tc_ha      = agb_tc_ha * plot_carbon_stock.root_shoot_ratio if agb_tc_ha is not None else 0.0

    if plot_carbon_stock.nontree_agb_tc_ha is not None:
        agb_tc_ha += plot_carbon_stock.nontree_agb_tc_ha
        agb_tdm_ha += plot_carbon_stock.nontree_agb_tc_ha / .47
    if plot_carbon_stock.nontree_bgb_tc_ha is not None:
        bgb_tc_ha += plot_carbon_stock.nontree_bgb_tc_ha
        bgb_tdm_ha += plot_carbon_stock.nontree_bgb_tc_ha / .47

    soc_tc_ha = plot_carbon_stock.soc_tc_ha
    deadwood_tc_ha = plot_carbon_stock.deadwood_tc_ha
    litter_tc_ha = plot_carbon_stock.litter_tc_ha


    ## Save to the plot
    plot_carbon_stock.estimated_n_trees = estimated_trees
    plot_carbon_stock.trees_ha = trees_ha
    plot_carbon_stock.dbh_mean = dbh_mean
    plot_carbon_stock.wsg_mean = wsg_mean
    plot_carbon_stock.height_mean = height_mean
    plot_carbon_stock.dbh_sd = dbh_sd
    plot_carbon_stock.wsg_sd = wsg_sd
    plot_carbon_stock.height_sd = height_sd
    plot_carbon_stock.agb_tdm_ha = agb_tdm_ha
    plot_carbon_stock.agb_tc_ha = agb_tc_ha
    plot_carbon_stock.bgb_tdm_ha = bgb_tdm_ha
    plot_carbon_stock.bgb_tc_ha = bgb_tc_ha
    plot_carbon_stock.data_valid = True
    plot_carbon_stock.save()
    print " Ending plot"
    return (agb_tc_ha, bgb_tc_ha, soc_tc_ha, litter_tc_ha, deadwood_tc_ha, agb_tdm_ha, bgb_tdm_ha, trees_ha)

#####################################################################################################################################################################################
def getReCalculateCarbons(request):
    try:
       myLevel =""
       aeq_id =6000
       input1 =  (request.GET.get('id')) 
        
       input2 = input1.replace('N', ' ')
       input3 = input2.split(' ')
       level = int(input3[0])
       PID = int(input3[1])
       input4 = input3[2]
       input4 = input4.strip()
       if len(input4)>0:
          aeq_id = int(input3[2])     
       print aeq_id   
       if level ==1 and aeq_id !=6000:       
    	   reCalculateTotalCarbonStocks(PID,aeq_id)       
           myLevel ="Good Work 1"
       if level ==2 and aeq_id !=6000:      
    	  reParcelCalculate(PID,aeq_id)
        # parcelCalculate(int(ParcelProperties))
          myLevel ="Good Work 2"
       if level ==3 and aeq_id !=6000:      
          rePlotCalculate(PID,aeq_id )
          plot=Plot.objects.get(id=PID)      
          parcel=Parcel.objects.get(id=plot.parcel_id)                          	    
          reParcelCalculate(parcel.id,aeq_id)                
          myLevel ="Good Work 3" 
    except Exception as e: 
          print e
    return HttpResponse(myLevel)




def reCalculateTotalCarbonStocks(project_id, aeq_id):
    print "here"
    '''
        This process will handle the calculations for an entire project.

        Calculating the carbon stocks for each parcel will be done on separate
        processes/threads as they can be done simulaneously.

        Calculating the carbon stocks for the project can only be done

        after each parcel has been calculated.
    '''

    project_carbon_stock = Project.objects.get(id=project_id)

    for parcel in project_carbon_stock.parcel_set.all():
        #----------------------------------------------
        parcelCalculate(parcel.id)
        #----------------------------------------------
        TreeAEQ.objects.filter(parcel=parcel).delete()
        p = parcelCalculate(parcel.id)
        project_carbon_stock.agb_tc      += Decimal(str(p.agb_tc)[:14])
        project_carbon_stock.bgb_tc      += Decimal(str(p.bgb_tc)[:14])
        project_carbon_stock.soc_tc      += Decimal(str(p.soc_tc)[:14])
        project_carbon_stock.deadwood_tc += Decimal(str(p.deadwood_tc)[:14])
        project_carbon_stock.litter_tc 	 += Decimal(str(p.litter_tc)[:14])
    
    b= project_carbon_stock._get_project_carbon_stocks()
    project_carbon_stock.total_tc = b.total_tc
    #print "All parcels calculated"
    project_carbon_stock.save()
    #print "Project saved"
    return True

def reParcelCalculate(parcel_id, aeq_id):
    print " in here"
    '''
        The purpose of this method is to do the carbon stock calculations for an individual parcel.
    '''
    def calculateParcelStatistics(biomass_list_data):
        '''
            This function will be used to calculate the statistics for the
            variance forms of biomass for parcels. It calculates the mean
            standard deviation, variance, t-statistic, and control chart

        '''

        if len(biomass_list_data) < 1:
            return (0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0)

        mean        = 0.0
        variance    = 0.0
        std         = 0.0
        t_statistic = 0.0
        n_plots     = 0
        min_95      = 0.0
        max_95      = 0.0
        perc_95     = 0.0

        mean     = numpy.mean(biomass_list_data)
        variance = numpy.var(biomass_list_data, ddof=1, dtype=float)

        if numpy.isnan(variance):
            variance = 0.0

        std            = numpy.sqrt(variance)
        n_plots        = len(biomass_list_data)
        standard_error = t_statistic = std / numpy.sqrt(n_plots)
        t_statistic    = scipy.stats.t.isf(0.025, n_plots - 1)

        if numpy.isnan(t_statistic):
            t_statistic = 0.0

        min_95  = mean - t_statistic * standard_error
        max_95  = mean + t_statistic * standard_error
        perc_95 = (max_95 / mean - 1) * 100

        return (mean, variance, std, n_plots, min_95, max_95, perc_95)

    parcel = Parcel.objects.get(id=parcel_id)
    #parcel.aeq_id =  aeq_id
    #parcel.save()
    
    plot_count = 0

    agb        = []
    bgb        = []
    soc        = []
    litter     = []
    deadwood   = []
    agb_tdm    = []
    bgb_tdm    = []
    trees_list = []

    variance_total = 0.0

    for p in parcel.plot_set.all():                 
        carbon_values = rePlotCalculate(p.id, p.aeq_id)       
        print carbon_values
        if carbon_values[0] is not None:
             agb.append(carbon_values[0])
        if carbon_values[1] is not None:
             bgb.append(carbon_values[1])
	if carbon_values[2] is not None:
	     soc.append(carbon_values[2])
	if carbon_values[3] is not None:
	     litter.append(carbon_values[3])
	if carbon_values[4] is not None:
	     deadwood.append(carbon_values[4])
	if carbon_values[5] is not None:
	     agb_tdm.append(carbon_values[5])
	if carbon_values[6] is not None:
	     bgb_tdm.append(carbon_values[6])
	if carbon_values[7] is not None:
	     trees_list.append(carbon_values[7])

    if any(agb):

        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(agb)

        parcel.mean_agb_tc_ha    = mean
        parcel.std_agb_tc_ha     = std
        parcel.n_plots_agb       = n_plots
        parcel.min_95_agb_tc_ha  = min_95
        parcel.max_95_agb_tc_ha  = max_95
        parcel.perc_95_agb_tc_ha = perc_95

        variance_total += variance


    if any(bgb):
        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(bgb)

        parcel.mean_bgb_tc_ha    = mean
        parcel.std_bgb_tc_ha     = std
        parcel.n_plots_bgb       = n_plots
        parcel.min_95_bgb_tc_ha  = min_95
        parcel.max_95_bgb_tc_ha  = max_95
        parcel.perc_95_bgb_tc_ha = perc_95

        variance_total += variance


    if any(soc):
        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(soc)

        parcel.mean_soc_tc_ha    = mean
        parcel.std_soc_tc_ha     = std
        parcel.n_plots_soc       = n_plots
        parcel.min_95_soc_tc_ha  = min_95
        parcel.max_95_soc_tc_ha  = max_95
        parcel.perc_95_soc_tc_ha = perc_95

        variance_total += variance

    if any(litter):
        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(litter)

        parcel.mean_litter_tc_ha    = mean
        parcel.std_litter_tc_ha     = std
        parcel.n_plots_litter       = n_plots
        parcel.min_95_litter_tc_ha  = min_95
        parcel.max_95_litter_tc_ha  = max_95
        parcel.perc_95_litter_tc_ha = perc_95

        variance_total += variance

    if any(deadwood):
        mean, variance, std, n_plots, min_95, max_95, perc_95 = calculateParcelStatistics(deadwood)

        parcel.mean_deadwood_tc_ha    = mean
        parcel.std_deadwood_tc_ha     = std
        parcel.n_plots_deadwood       = n_plots
        parcel.min_95_deadwood_tc_ha  = min_95
        parcel.max_95_deadwood_tc_ha  = max_95
        parcel.perc_95_deadwood_tc_ha = perc_95

        variance_total += variance

    if any(agb_tdm):
        parcel.mean_agb_tdm_ha = numpy.mean(agb_tdm)
        parcel.std_agb_tdm_ha  = numpy.std(agb_tdm, ddof=1, dtype=float)
        if numpy.isnan(parcel.std_agb_tdm_ha):
            parcel.std_agb_tdm_ha = 0.0
    if any(bgb_tdm):
        parcel.mean_bgb_tdm_ha = numpy.mean(bgb_tdm)
        parcel.std_bgb_tdm_ha  = numpy.std(bgb_tdm, ddof=1, dtype=float)
        if numpy.isnan(parcel.std_bgb_tdm_ha):
            parcel.std_bgb_tdm_ha = 0.0
    if any(trees_list):
        parcel.mean_trees_ha = numpy.mean(trees_list)
        parcel.std_trees_ha  = numpy.std(trees_list, ddof=1, dtype=float)
        if numpy.isnan(parcel.std_trees_ha):
            parcel.std_trees_ha = 0.0

    parcel.save()
    return parcel

def rePlotCalculate(plot_id, aeq_id):

    def sumOfSquares(square, reg, mean, count):
        return square-(2*mean*reg)+(count*mean**2) if count else 0.0

    def extrapolate(value, area, subplot_area):
        return value * area / subplot_area if subplot_area else 0.0

    def calculate_tree_agb(tree, area, subplot_area):
        equations = None
        equationspecies = None
        species = tree.species
        genus = tree.genus

        if tree.plot.calculate_by_species:
            if genus and tree.plot.region:
                try:
                    equationspecies = allometric.models.EquationSpecies.objects.get(genus__iexact=genus, name__iexact=species)
                except Exception as e:
                    try:
                        equationspecies = allometric.models.EquationSpecies.objects.get(genus__iexact=genus, name='species')
                    except:
                        equationspecies=None

            try:
                if not tree.plot.region:
                    raise Exception('No region')
                equations = allometric.models.Equation.objects.filter(id=aeq_id)
                if not equations:
                    equations = allometric.models.Equation.objects.filter(id=aeq_id)
                    #this is grabbing all the equations for a region.  don't we want it to grab the default equation for the region only?

                if not equations or len(equations) == 0:
                    if tree.plot.region.name in DEFAULT_REGION_EQUATIONS:
                       c = allometric.models.Equation()
                       c.string = DEFAULT_REGION_EQUATIONS[tree.plot.region.name]
                       equations = [c]
                if not equations:
                    raise Exception('No equation available')
            except:
                equations = allometric.models.Equation.objects.filter(id=aeq_id)
        else:
            equations = allometric.models.Equation.objects.filter(id=aeq_id)

        # if tree.plot.calculate_by_species:
        #     equations = tree.aeqs.all()
        #     print equations
        # else:
        #     equations = [tree.plot.get_aeq()]

        agb_kg_dm = 0.0
        equation_list_objects = list()
        for eq in equations:
            temp = eq._calculate_agb(tree)
            if eq.volumetric:
                #if tree.wood_gravity:
                #    temp = temp * tree.wood_gravity * 1000 #gives kg of biomass
            	#elif equationspecies.wood_gravity:
            	#	temp = temp * equationspecies.wood_gravity * 1000
                #else:
                if tree.wood_gravity:
                    temp = temp * tree.wood_gravity * 1000
                else:
                    temp = temp * 0.7 * 1000 #gives kg of biomass
            elif eq.less_than_ten:
                if not eq.is_less_than_dbh(tree.dbh):
                    temp = 0
            elif not eq.less_than_ten:
                if eq.is_less_than_dbh(tree.dbh) and eq.region:
                    temp = 0
            agb_kg_dm += temp
            if eq.id:
                c = TreeAEQ(tree=tree, aeq=eq, parcel=tree.plot.parcel, plot=tree.plot)
                equation_list_objects.append(c)

        TreeAEQ.objects.bulk_create(equation_list_objects)
        if agb_kg_dm == 0.0:
            tree.used_in_calculations = False
            tree.comments = "Tree not used in calculations"
            tree.save()
        return agb_kg_dm


    '''
        The purpose of this method is to do the carbon stock calculations for an individual plot.
    '''
    plot_carbon_stock = Plot.objects.get(id=plot_id)
    plot_carbon_stock.aeq_id = aeq_id;

    Trees = plot_carbon_stock.tree_set.all()

    subplots = [plot_carbon_stock.subplot_1_area, plot_carbon_stock.subplot_2_area, plot_carbon_stock.subplot_3_area, plot_carbon_stock.area]
    estimated_trees = 0.0
    trees_ha        = 0.0

    # These are the variables that we will use to store the
    # overall calculations
    dbh_mean          = 0.0
    height_mean       = 0.0
    wsg_mean          = 0.0

    dbh_sd            = 0.0
    height_sd         = 0.0
    wsg_sd            = 0.0

    dbh             = [ 0.0, 0.0, 0.0, 0.0 ]
    dbh_sq          = [ 0.0, 0.0, 0.0, 0.0 ]
    height          = [ 0.0, 0.0, 0.0, 0.0 ]
    height_sq       = [ 0.0, 0.0, 0.0, 0.0 ]
    wsg             = [ 0.0, 0.0, 0.0, 0.0 ]
    wsg_sq          = [ 0.0, 0.0, 0.0, 0.0 ]
    trees           = [ 0.0, 0.0, 0.0, 0.0 ]
    agb_kg_dm       = [ 0.0, 0.0, 0.0, 0.0 ]

    for t in Trees:
        if t.dbh is None:
            continue
        elif t.dbh > plot_carbon_stock.subplot_1_lower_bound and t.dbh <= plot_carbon_stock.subplot_1_upper_bound:
            print "elif 1"
            agb_kg_dm[0] += calculate_tree_agb(t, plot_carbon_stock.area, plot_carbon_stock.subplot_1_area)
            trees[0] += 1

            dbh[0]                += t.dbh
            dbh_sq[0]             += t.dbh**2

            height[0]             += t.total_height if t.total_height else 0.0
            height_sq[0]          += t.total_height**2 if t.total_height else 0.0

            wsg[0]                += t.wood_gravity if t.wood_gravity else 0.0
            wsg_sq[0]             += t.wood_gravity if t.wood_gravity else 0.0
        elif t.dbh > plot_carbon_stock.subplot_2_lower_bound and t.dbh <= plot_carbon_stock.subplot_2_upper_bound:
            print "elif 2"
            agb_kg_dm[1] += calculate_tree_agb(t, plot_carbon_stock.area, plot_carbon_stock.subplot_2_area)
            trees[1] += 1

            dbh[1]                += t.dbh
            dbh_sq[1]             += t.dbh**2

            height[1]             += t.total_height if t.total_height else 0.0
            height_sq[1]          += t.total_height**2 if t.total_height else 0.0

            wsg[1]                += t.wood_gravity if t.wood_gravity else 0.0
            wsg_sq[1]             += t.wood_gravity**2 if t.wood_gravity else 0.0
        elif t.dbh > plot_carbon_stock.subplot_3_lower_bound and t.dbh <= plot_carbon_stock.subplot_3_upper_bound:
            print "elif 3"
            agb_kg_dm[2] += calculate_tree_agb(t, plot_carbon_stock.area, plot_carbon_stock.subplot_3_area)
            trees[2] += 1

            dbh[2]                += t.dbh
            dbh_sq[2]             += t.dbh**2

            height[2]             += t.total_height if t.total_height else 0.0
            height_sq[2]          += t.total_height**2 if t.total_height else 0.0

            wsg[2]                += t.wood_gravity if t.wood_gravity else 0.0
            wsg_sq[2]             += t.wood_gravity**2 if t.wood_gravity else 0.0
        else:
            agb_kg_dm[3] += calculate_tree_agb(t, plot_carbon_stock.area, plot_carbon_stock.area)
            trees[3] += 1

            dbh[3]                += t.dbh
            dbh_sq[3]             += t.dbh**2

            height[3]             += t.total_height if t.total_height else 0.0
            height_sq[3]          += t.total_height**2 if t.total_height else 0.0

            wsg[3]                += t.wood_gravity if t.wood_gravity else 0.0
            wsg_sq[3]             += t.wood_gravity**2 if t.wood_gravity else 0.0

    #estimated_trees = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(trees, subplots)])
    estimated_trees = trees[0] + trees[1] + trees[2] + trees[3]
    if plot_carbon_stock.area is not None and plot_carbon_stock.area != 0.0:
        trees_ha = estimated_trees / plot_carbon_stock.area
    else:
        trees_ha = None

    height_mean = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(height, subplots)]) / estimated_trees if estimated_trees else 0.0
    dbh_mean    = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(dbh, subplots)]) / estimated_trees if estimated_trees else 0.0
    wsg_mean    = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(wsg, subplots)]) / estimated_trees if estimated_trees else 0.0

    dbh_sum_sq    = sum([extrapolate(sumOfSquares(x,y,dbh_mean,z),plot_carbon_stock.area,w) for w,x,y,z in zip(subplots, dbh_sq, dbh, trees)])
    height_sum_sq = sum([extrapolate(sumOfSquares(x,y,height_mean,z),plot_carbon_stock.area,w) for w,x,y,z in zip(subplots, height_sq, height, trees)])
    wsg_sum_sq    = sum([extrapolate(sumOfSquares(x,y,wsg_mean,z),plot_carbon_stock.area,w) for w,x,y,z in zip(subplots, wsg_sq, wsg, trees)])

    height_sd = numpy.sqrt(height_sum_sq / (estimated_trees - 1)) if estimated_trees and estimated_trees > 1 else 0.0

    dbh_sd    = numpy.sqrt(dbh_sum_sq / (estimated_trees - 1)) if estimated_trees and estimated_trees > 1 else 0.0
    wsg_sd    = numpy.sqrt(wsg_sum_sq / (estimated_trees - 1)) if estimated_trees and estimated_trees > 1 else 0.0

    sum_agb_kg_dm = sum([extrapolate(x, plot_carbon_stock.area, y) for x,y in zip(agb_kg_dm, subplots)])

    agb_tdm_ha     = (sum_agb_kg_dm / 1000.0) / plot_carbon_stock.area if plot_carbon_stock.area else 0.0
    agb_tc_ha      = (sum_agb_kg_dm / 1000.0 * .47) / plot_carbon_stock.area if plot_carbon_stock.area else 0.0

    bgb_tdm_ha     = agb_tdm_ha * plot_carbon_stock.root_shoot_ratio if agb_tdm_ha is not None else 0.0
    bgb_tc_ha      = agb_tc_ha * plot_carbon_stock.root_shoot_ratio if agb_tc_ha is not None else 0.0

    if plot_carbon_stock.nontree_agb_tc_ha is not None:
        agb_tc_ha += plot_carbon_stock.nontree_agb_tc_ha
        agb_tdm_ha += plot_carbon_stock.nontree_agb_tc_ha / .47
    if plot_carbon_stock.nontree_bgb_tc_ha is not None:
        bgb_tc_ha += plot_carbon_stock.nontree_bgb_tc_ha
        bgb_tdm_ha += plot_carbon_stock.nontree_bgb_tc_ha / .47

    soc_tc_ha = plot_carbon_stock.soc_tc_ha
    deadwood_tc_ha = plot_carbon_stock.deadwood_tc_ha
    litter_tc_ha = plot_carbon_stock.litter_tc_ha


    ## Save to the plot
    plot_carbon_stock.estimated_n_trees = estimated_trees
    plot_carbon_stock.trees_ha = trees_ha
    plot_carbon_stock.dbh_mean = dbh_mean
    plot_carbon_stock.wsg_mean = wsg_mean
    plot_carbon_stock.height_mean = height_mean
    plot_carbon_stock.dbh_sd = dbh_sd
    plot_carbon_stock.wsg_sd = wsg_sd
    plot_carbon_stock.height_sd = height_sd
    plot_carbon_stock.agb_tdm_ha = agb_tdm_ha
    plot_carbon_stock.agb_tc_ha = agb_tc_ha
    plot_carbon_stock.bgb_tdm_ha = bgb_tdm_ha
    plot_carbon_stock.bgb_tc_ha = bgb_tc_ha
    plot_carbon_stock.data_valid = True
    plot_carbon_stock.save()   

    return (agb_tc_ha, bgb_tc_ha, soc_tc_ha, litter_tc_ha, deadwood_tc_ha, agb_tdm_ha, bgb_tdm_ha, trees_ha)
#####################################################################################################################################################################################

