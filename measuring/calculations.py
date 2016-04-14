
DEFAULT_REGION_EQUATIONS = {
    'Central Highlands' : '7.420770 (dbh/100)^2 - 0.838878 (dbh/100) + 0.023708',
    'North-Eastern Ranges' : '0.15958 - 1.57976 (dbh/100) + 8.25014 (dbh/100)^2 - 0.48518 (dbh/100)^3',
    'East Coast' : '8.760534 (dbh/100)^2 - 1.449236 (dbh/100) + 0.088074',
    'Western Plain' : '0.081467 - 1.063661 (dbh/100) + 6.452918 (dbh/100)^2',
    'East Deccan' : '8.760534 (dbh/100)^2 - 1.449236 (dbh/100) + 0.088074',
    'South Deccan' : '0.088183 - 1.490948 (dbh/100) + 8.984266 (dbh/100)^2'
}

ACTIONS {
    'ADD' : 0,
    'DEL' : 1,
    'CHANGE' : 3,
    'RECALC' : 4,
}

@shared_task
def calculateCarbonStocks(project_id, action, parcel_id = None):
    project_carbon_stock = ProjectCarbonStock.objects.get(project=project_id)

    if  parcel_id is not None 
        parcel_carbon_stock = ParcelCarbonStockTierThree.objects.get(parcel=parcel_id)

    if parcel_id is None and (action == 0 or action == 1 or action == 3):
        raise Exception("No parcel was entered. Recalculate")

    if action == ACTIONS['ADD']:
        project_carbon_stocks.agb_tc += Decimal(str(parcel_carbon_stock.agb_tc)[:14])
        project_carbon_stocks.bgb_tc += Decimal(str(parcel_carbon_stock.bgb_tc)[:14])
        project_carbon_stocks.soc_tc += Decimal(str(parcel_carbon_stock.soc_tc)[:14])
        project_carbon_stocks.deadwood_tc += Decimal(str(parcel_carbon_stock.deadwood_tc)[:14])
        project_carbon_stocks.litter_tc += Decimal(str(parcel_carbon_stock.litter_tc)[:14])
    elif action == ACTIONS['DEL']:
        project_carbon_stocks.agb_tc -= Decimal(str(parcel_carbon_stock.agb_tc)[:14])
        project_carbon_stocks.bgb_tc -= Decimal(str(parcel_carbon_stock.bgb_tc)[:14])
        project_carbon_stocks.soc_tc -= Decimal(str(parcel_carbon_stock.soc_tc)[:14])
        project_carbon_stocks.deadwood_tc -= Decimal(str(parcel_carbon_stock.deadwood_tc)[:14])
        project_carbon_stocks.litter_tc -= Decimal(str(parcel_carbon_stock.litter_tc)[:14])
    elif action == ACTIONS['RECALC']:
        pass
    else:
        raise Exception("Incorrect action type")

    project_carbon_stocks.save()


def calculateParcelStocks(parcel_id, action, plot_id = None):
    pass


def calculatePlotStocks(plot_id):
    def sum_of_squares(square, reg, mean, count):
        return square - (2 * mean * reg) + (count * mean**2) if count else 0.0

    def extrapolate(value, area, subplot_area):
        return value * area / subplot_area if subplot_area else 0.0

    def calculate_agb(tree, area, subplot_area):
        equations = None
        equationspecies = None
        species = tree.species
        genus = tree.genus
        region = tree.plot.region