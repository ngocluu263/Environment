from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from ecalc.models import Scenario


#@csrf_exempt
def serve_scenario_graph(request, project_id, scenario_id):
    scenario = get_object_or_404(Scenario, id=scenario_id)
    if scenario.project.user == request.user:  # verify that user has PERMISSIONS OWNERSHIP of scenario

        # 1) List-ify data
        x = list()  # list()
        y = list(list() for i in range(4))  # list of 4 nested lists
        #y2 = list(list() for i in range(3))  # list of 3 nested lists
        y_value_initial = None
        y_value_final = None
        for cp in scenario.carbonpools_set.all():
            y[0].append(cp.GetBiomass)
            y[1].append(cp.GetSoil)
            y[2].append(cp.GetDeadCarbon)
            y[3].append(cp.GetHarvested)
            #y2[0].append(cp.annual_emissions)
            #y2[1].append(cp.annual_nonco2)
            #y2[2].append(cp.GetAtm)
            x.append(cp.year)
        else:  # case: last loop
            y_value_final = cp.GetAtm


        # 2) Create matplotlib plot
        fig1 = plt.figure(figsize=(5, 3.7))
        ax1 = fig1.add_subplot(1, 1, 1)

        # colors (scheme @ http://colorschemedesigner.com/#2M41Tw0w0w0w0)
        colors = ["#389E28", "#1E776D", "#BF6D30", "#BA2F39"]

        # render plot
        ax1.stackplot(x, y[0], y[1], y[2], y[3], colors=colors)

        # render legend
        labels = ["Biomass", "Soil", "Dead Carbon", "HWP"]
        proxies = [Rectangle((0, 0), 1, 1, color=colors[j]) for j in range(4)]  # create proxy objects as stackplot() does not generate legend label
        ax1.legend(proxies, labels, 'lower right')

        ax1.set_title('Carbon Pools (stacked)')
        ax1.set_xlabel('Project Year')
        ax1.set_ylabel('Carbon Stocks (tC)')

        ax1.grid(True)

        # render text label expressing delta-tCO2e (atmospheric emissions)
        text = ax1.text(.95, .925, "$\Delta$ Atmosphere: %+.0f tCO2e" % y_value_final, transform=ax1.transAxes, ha='right', backgroundcolor="#34CFBE")

        # create second subplot for tCO2e (at right axis)
        #ax2 = fig1.add_subplot(1, 1, 1, sharex=ax1, frameon=False)
        #ax2.yaxis.tick_right()
        #ax2.yaxis.set_label_position('right')
        #ax2.set_ylabel('Change in Atmospheric Carbon (tCO2e)')
        #ax2.plot(x, y2[0], label='Annual CO2 Emissions')
        #ax2.plot(x, y2[1], label='Annual Non-CO2 Emissions')
        #ax2.plot(x, y2[2], label='Cumulative Emissions')
        # convert tC scale to tCO2e scale!
        #axis = ax1.axis()
        #ax2.axis([axis[0], axis[1], axis[3] * 44 / 12], axis[2])

        # 3) Save graph to response
        response = HttpResponse(content_type='image/png')
        fig1.savefig(response, bbox_inches='tight', dpi=100)

        # 4) return response
        return response
    else:
        raise Http404
