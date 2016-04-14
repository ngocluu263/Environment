
$(document).ready(function() {
    parcelid = $('#parcelDropdown').val();
    parcelChanged();
});

$('#parcelDropdown').on('change', function(event){
    parcelid = $(this).val();
    parcelChanged();
})

function parcelChanged()
{
    if( parcelid == '')
    {
        $("#t1StocksLink").hide(300);
        $("#t2StocksLink").hide(300);
        $("#plotSummaryLink").hide(300);
        $("#carbonStocksPlotLink").hide(300);

        $("#t1Instructions").show(300);
        $("#t2Instructions").show(300);
        $("#step10instruction").show(300);
        $("#step11instruction").show(300);
        $('#equationsRow').hide(300);
    }
    else
    {
        $("#t1StocksLink").show(300);
        $("#t2StocksLink").show(300);
        $("#plotSummaryLink").show(300);
        $("#carbonStocksPlotLink").show(300);

        $("#t1Instructions").hide(300);
        $("#t2Instructions").hide(300);
        $("#step10instruction").hide(300);
        $("#step11instruction").hide(300);
        $("#equationsRow").show(300);


        $.ajax({
            dataType: 'json',
            url: '/api/v1/parcel-carbon-stocks-t1/' + parcelid + '/',
            type: 'GET',
            success: fillT1CarbonData
        })

        $.ajax({
            dataType: 'json',
            url: '/api/v1/parcel-carbon-stocks-t2/' + parcelid + '/',
            type: 'GET',
            success: fillT2CarbonData
        })

        $.ajax({
            dataType: 'json',
            url: '/api/v1/parcel-carbon/' + parcelid  + '/',
            type: 'GET',
            beforeSend: function() { $(".overlay").fadeIn(); },
            complete: function() { $(".overlay").fadeOut(); },
            success: fillPlotSummary
        })
    }

}

function tier1Stocks()
{
    console.log("tier 1 stocks");
    $("#myModal").load("carbon_stocks_tier_one.html", function() {
        $("#myModal").modal("show");
    });
}

function numberWithCommas(x) {
    var parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
}

// used to fill in the data for tier 1 or tier 2 carbon data
function fillCarbonData(data, tag)
{
    $("#" + tag + "_name").html(data['name']);
    $("#" + tag + "_area").html(numberWithCommas(parseFloat(data['area_used']).toFixed(2)));

    $("#" + tag + "_agb").html(numberWithCommas(parseFloat(data['mean_agb_tc_ha']).toFixed(2)));
    $("#" + tag + "_bgb").html(numberWithCommas(parseFloat(data['mean_bgb_tc_ha']).toFixed(2)));
    $("#" + tag + "_soc").html(numberWithCommas(parseFloat(data['mean_soc_tc_ha']).toFixed(2)));
    $("#" + tag + "_litter").html(numberWithCommas(parseFloat(data['mean_litter_tc_ha']).toFixed(2)));
    $("#" + tag + "_deadwood").html(numberWithCommas(parseFloat(data['mean_deadwood_tc_ha']).toFixed(2)));

    $("#" + tag + "_agb_tc").html(numberWithCommas(parseFloat(data['agb_tc']).toFixed(2)));
    $("#" + tag + "_bgb_tc").html(numberWithCommas(parseFloat(data['bgb_tc']).toFixed(2)));
    $("#" + tag + "_soc_tc").html(numberWithCommas(parseFloat(data['soc_tc']).toFixed(2)));
    $("#" + tag + "_litter_tc").html(numberWithCommas(parseFloat(data['litter_tc']).toFixed(2)));
    $("#" + tag + "_deadwood_tc").html(numberWithCommas(parseFloat(data['deadwood_tc']).toFixed(2)));
    $("#" + tag + "_total_tc").html(numberWithCommas(parseFloat(data['total_tc']).toFixed(2)));                
}

function createCarbonRow(tag)
{
    return '<tr> \
                <td id="' + tag + '_name"></td> \
                <td id="' + tag + '_area"></td> \
                <td id="' + tag + '_agb"></td> \
                <td id="' + tag + '_bgb"></td> \
                <td id="' + tag + '_soc"></td> \
                <td id="' + tag + '_litter"></td> \
                <td id="' + tag + '_deadwood"></td> \
                <td id="' + tag + '_agb_tc"></td> \
                <td id="' + tag + '_bgb_tc"></td> \
                <td id="' + tag + '_soc_tc"></td> \
                <td id="' + tag + '_litter_tc"></td> \
                <td id="' + tag + '_deadwood_tc"></td> \
                <td id="' + tag + '_total_tc"></td> \
            </tr>';
}

function createPlotSummaryRow(plot, parcel_name)
{
    var name = plot['name'];
    var area = numberWithCommas((parseFloat(plot['area'])*10000).toFixed(2));
    var inv_trees = plot['inventory_n_trees'];
    var est_trees = plot['estimated_n_trees'];
    var dbh = plot['dbh_mean'];
    var height = plot['height_mean'];
    var wsg = plot['wsg_mean'];
    var rs_ratio = plot['root_shoot_ratio'];
    var aeq = plot['allometric_equation'];

    if(inv_trees == null)
        inv_trees = "—";
    else
        inv_trees = numberWithCommas(parseFloat(inv_trees).toFixed(0));

    if(est_trees == null)
        est_trees = "—";
    else
        est_trees = numberWithCommas(parseFloat(est_trees).toFixed(0));

    if(dbh == null)
        dbh = "—";
    else
        dbh = numberWithCommas(parseFloat(dbh).toFixed(2)).concat(" &plusmn; " + numberWithCommas(parseFloat(plot['dbh_sd']).toFixed(2)));

    if(height == null)
        height = "—";
    else
        height = numberWithCommas(parseFloat(height).toFixed(2)).concat(" &plusmn; " + numberWithCommas(parseFloat(plot['height_sd']).toFixed(2)));

    if(wsg == null)
        wsg = "—";
    else
        wsg = numberWithCommas(parseFloat(wsg).toFixed(2)).concat(" &plusmn; " + numberWithCommas(parseFloat(plot['wsg_sd']).toFixed(2)));

    if(rs_ratio == null)
        rs_ratio = "—";
    else
        rs_ratio = numberWithCommas(parseFloat(rs_ratio).toFixed(2));


    var newRow =    '<tr> \
                        <td>' + parcel_name + '</td> \
                        <td>' + name + '</td> \
                        <td>' + area + '</td> \
                        <td>' + inv_trees + '</td> \
                        <td>' + est_trees + '</td> \
                        <td>' + dbh + '</td> \
                        <td>' + height + '</td> \
                        <td>' + wsg + '</td> \
                        <td>' + rs_ratio + '</td> \
                        <td>' + aeq + '</td> \
                    </tr>';
    $("#plots_summary_data_rows").html($("#plots_summary_data_rows").html() + newRow);
}

function createPlotCarbonRow(plot, parcel_name)
{
    var name = plot['name'];
    var area = (numberWithCommas((parseFloat(plot['area']) * 10000).toFixed(2)));
    var trees = plot['trees_ha'];
    var agb = plot['agb_tc_ha'];
    var bgb = plot['bgb_tc_ha'];
    var soc = plot['soc_tc_ha'];
    var litter = plot['litter_tc_ha'];
    var deadwood = plot['deadwood_tc_ha'];
    var total = plot['total_tc_ha'];


    if(trees == null)
        trees = "—";
    else
        trees = numberWithCommas(parseFloat(trees).toFixed(0));

    if(agb == null)
        agb = "—";
    else
        agb = numberWithCommas(parseFloat(agb).toFixed(2));

    if(bgb == null)
        bgb = "—";
    else
        bgb = numberWithCommas(parseFloat(bgb).toFixed(2));

    if(soc == null)
        soc = "—";
    else
        soc = numberWithCommas(parseFloat(soc).toFixed(2));

    if(litter == null)
        litter = "—";
    else 
        litter = numberWithCommas(parseFloat(litter).toFixed(2));

    if(deadwood == null)
        deadwood = "—";
    else
        deadwood = numberWithCommas(parseFloat(deadwood).toFixed(2));

    if(total == null)
        total = "—";
    else
        total = numberWithCommas(parseFloat(total).toFixed(2));


    var newRow =    '<tr> \
                        <td>' + parcel_name + '</td> \
                        <td>' + name + '</td> \
                        <td>' + area + '</td> \
                        <td>' + trees + '</td> \
                        <td>' + agb + '</td> \
                        <td>' + bgb + '</td> \
                        <td>' + soc + '</td> \
                        <td>' + litter + '</td> \
                        <td>' + deadwood + '</td> \
                        <td>' + total + '</td> \
                    </tr>';
    $("#plots_stocks_data_rows").html($("#plots_stocks_data_rows").html() + newRow);
}

function fillPlotCarbonTotalRow(parcel)
{
    $("#stocks_plots_trees").html(numberWithCommas(parseFloat(parcel['mean_trees_ha']).toFixed(0)));
    $("#stocks_plots_agb").html(numberWithCommas(parseFloat(parcel['mean_agb_tc_ha']).toFixed(2)));
    $("#stocks_plots_bgb").html(numberWithCommas(parseFloat(parcel['mean_bgb_tc_ha']).toFixed(2)));
    $("#stocks_plots_soc").html(numberWithCommas(parseFloat(parcel['mean_soc_tc_ha']).toFixed(2)));
    $("#stocks_plots_litter").html(numberWithCommas(parseFloat(parcel['mean_litter_tc_ha']).toFixed(2)));
    $("#stocks_plots_deadwood").html(numberWithCommas(parseFloat(parcel['mean_deadwood_tc_ha']).toFixed(2)));
    $("#stocks_plots_total").html(numberWithCommas(parseFloat(parcel['total_tc_ha'][0]).toFixed(2)));
}

function createEquationsRow(plot, parcel_name)
{
    var newRow = '<tr> \
                    <td colspan="5" class="success"><b>Plot: ' + plot["name"] + '</b></td> \
                  </tr> \
                  <tr> \
                        <th>Tree ID</th> \
                        <th>Tree Species</th> \
                        <th>Name</th> \
                        <th>Equation</th> \
                        <th>Region</th> \
                  </tr>';

    
    if (plot["treeaeqs"])
    {
        console.log("plot['equation']:");
    }
    $('#equationsTable').append(newRow);

    $.each(plot["treeaeqs"], function(index, eq){
        createEquation(eq);
    });
}

function createEquation(equation)
{

        var newRow = '<tr> \
                     <td>' + equation["tree"]["id"] + '</td> \
                    <td><i>' + equation["tree"]["genus"] + ' ' + equation["tree"]["species"] + '</i></td> \
                    <td>' + equation["aeq"]["name"] + '</td> \
                    <td>' + equation["aeq"]["string"] + '</td>'
    if (equation["aeq"]["region"])
        newRow += '<td>' + equation["aeq"]["region"]["name"] + '</td></tr>';
    else
        newRow += '<td></td>';
    $('#equationsTable').append(newRow);
}

function fillT1CarbonData(data)
{
    fillCarbonData(data, 't1');
}

function fillT2CarbonData(data)
{
    fillCarbonData(data, 't2');
}

function fillParcelCarbonData(data)
{
    console.log("fill parcel carbon data");
    var tag = "parcel_" + data['id'];
    var newRow = createCarbonRow(tag);
    $("#stocksTable").html($("#stocksTable").html() + newRow);
    fillCarbonData(data, tag);
}

// fills all tables that use plots based on selected parcel
function fillPlotSummary(data)
{
    $('#equationsTable').html("");
    $("#plots_summary_data_rows").html("");
    $("#plots_stocks_data_rows").html("");
    var parcel_name = data['name'];
    console.log('here');
    var plotsData = data["plots"];
    var plotsData2 = plotsData.sort(compare);
    // foreach plot in parcel
    $.each(plotsData2, function( index, plot) {
        console.log(plot);
        createPlotSummaryRow(plot, parcel_name);
        console.log('here');
        createPlotCarbonRow(plot, parcel_name);
        console.log('carbon row')
        //createEquationsRow(plot, parcel_name);
        console.log('eq row');
        fillPlotCarbonTotalRow(data);
    });
}

function compare(a,b) {
  if (a.name < b.name)
    return -1;
  else if (a.name> b.name)
    return 1;
  else 
    return 0;
}
