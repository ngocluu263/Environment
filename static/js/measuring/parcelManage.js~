//************************************************************************
    //              Declare some variables that we will use on this page
    //
    var projectID;
    var reportedArea;
    var parcelReportedArea;
    var parcelid;
    var parcels;
    var plotid;
    var dataSet;
    


    //***********************************************************************
    //
    //      Pass in some important context variables that we will
    //      need.
    //      PARAMS:
    //          projectid -- The id for the projct we are working on
    function variablePassIn(projectid) {
        projectID = projectid;
    }

    //
    //***********************************************************************
    //
    //
    //***********************************************************************
    //             These are our methods for handling the process
    //             of getting a csrf token for submitting our forms
    //
    //
    // Get the CSRF cookie so we can submit the form. This is to prevent
    // cross site request forgery
    //
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        function sameOrigin(url) {
            // test that a given url is a same-origin URL
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }

    //
    //****************************************************************************
    //
    //****************************************************************************
    //          Do some initial page formatting before the document loads
    //
        // $('#reportedAreaDirections').hide();
        $('#parcelInformation').hide();
        $('#parcelreportedareawarning').hide();
    //
    //***************************************************************************
    //
    //***************************************************************************
    //          These are the functions to call when the form
    //          ajax submit has been successful or failed
    //

        function notValid(data)
        {
            $('#ajaxMessages').html('<div class="alert alert-danger alert-dismissable"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button><strong>Error!</strong> ' + data + ' is invalid. Form did not submit.</div>');
        }

        function getPlots(url)
        {
            if (url == null || url === undefined)
                url = '/api/v1/plot/?order_by=name&parcel=' + parcelid;

            $('#parcelInformation').show(300);

            $('#plotInformationNoParcel').hide(300);

            $.ajax({
                type: 'GET',
                url: url,
                dataType: 'json',
                
                success: ajaxGetPlotSuccess
            })
        }

        function ajaxGetPlotSuccess(data)
        {
            var plotSelect = null;

            if (data['meta']['offset'] == 0 && data['meta']['total_count'] != 0) {
                $('#plotInformationDDPanel').empty();
                plotSelect = $("<select id=\"plotDropdown\" class=\"form-control\" />");
                $('#plotInformationDDPanel').append(plotSelect);
            } else if (data['meta']['total_count'] == 0) {
                $('#plotInformationDDPanel').html("<div id=\"noPlots\" style=\"margin-top:.5em;\"><em>There are no plots associated with this parcel</em></div>");
                $('#plotInformation').show(300);
                return;
            } else if (data['meta']['offset'] > 0) {
                plotSelect = $("plotDropdown");
            }

            $("<option />", {value: '', text: 'Select a Plot'}).appendTo(plotSelect);
            objects.sort();
            $.each(data['objects'], function( key, value ){
                $("<option />", {value: value['id'], text: value['name']}).appendTo(plotSelect);
            })

            plotSelect.on('change', function(event){
                if (plotSelect.val() == '')
                {
                    $('#detailsButton').addClass('disabled');
                }
                else
                {
                    $('#detailsButton').removeClass('disabled');
                    $('#detailsButton').attr("href", "/measuring/parcel_management/plot_details/" + plotSelect.val() + "/");
                }
            })


            if (data['meta']['next'] != null)
                getPlots(data['meta']['next']);
            else
                $('#plotInformation').show(300);

        }
    

    //**************************************************************************
    $(document).ready(function(){
        // Hide the message stating that areas will be rounded to
        // four decimal places
        // Save the current reported area
        reportedArea = $('#reported_area_project').val();

        parcelid = $("#parcelDropdown").val();
        parcelChanged();

        var el = $();

        
        // @Event
        // Name: Display
        // DOM ELEMENT/ID: DIV/reportedAreaDirections
        // Purpose: Displays the submit/cancel buttons and 2 decimal places warning
        $('#reportedAreaDirections').on('display', function(event){
            var displayHtml = '<div class="col-sm-9">' + 
            '<span style="color:red;">' +
            '<em>The area you enter will be rounded to 2 decimal places</em></span></div>' +
            '<div class="col-sm-3">' +
            '<button type="button" id="reportedFormCancel" class="btn btn-primary btn-sm">Cancel</button>' +
            '<input type="submit" value="Submit" class="btn btn-danger btn-sm" style="margin-left:5px;"/>'
            '</div>';
            $(this).html(displayHtml);
            $(this).show(300);
            $('#reportedFormCancel').on('click', function(event){

                // Set the reported area value back to the previous value
                $('#reported_area_form')[0].reset();
                $('#reportedAreaDirections').trigger('disappear');
            });
        });


        // @Event
        // Name: Display
        // DOM ELEMENT/ID: DIV/parcelReportedAreaWarn
        // Purpose: Displays the submit/cancel buttons and 2 decimal places warning
        $('#parcelReportedAreaWarn').on('display', function(event){
            console.log('In here');
            var displayHtml = '<div class="col-sm-9">' + 
            '<span style="color:red;">' +
            '<em>The area you enter will be rounded to 2 decimal places</em></span></div>' +
            '<div class="col-sm-3">' +
            '<button type="button" id="parcelReportedFormCancel" class="btn btn-primary btn-sm">Cancel</button>' +
            '<input type="submit" value="Submit" class="btn btn-danger btn-sm" style="margin-left:5px;" />'
            '</div>';
            $(this).html(displayHtml);
            $(this).show(300);
            $('#parcelReportedFormCancel').on('click', function(event){

                // Set the reported area value back to the previous value
                $('#parcelReportedForm')[0].reset();
                $('#parcelReportedAreaWarn').trigger('disappear');
            })
        });

        // @Event
        // Name: Display
        // DOM ELEMENT/ID: DIV/parcelInformation
        // Purpose: Displays the details for the selected parcel from the dropdown menu
        $('#parcelInformation').on('display', function(event, parcel, mappedArea, tempReportedArea){
            var mappedArea = parseFloat(mappedArea).toFixed(2);
            console.log("tempReportedArea: " + tempReportedArea);
            if ( parcel != '' )
            {
                var displayHtml = '<div class="col-sm-3">' +
                '<label style="font-weight:normal; margin-top:.5em;">Mapped Area:</label>' +
                '</div><div class="col-sm-3">' +
                '<div style="margin-top:.5em;">' + mappedArea + '</div></div>' +
                '<div class="col-sm-3">' +
                '<label style="font-weight:normal; margin-top:.5em;">Reported Area (ha):</label></div>' +
                '<div class="col-sm-3">';
                if(tempReportedArea != '')
                    displayHtml += '<input id="parcelReportedAreaInput" name="parcelreportedarea" type="text" value=' + tempReportedArea + ' class="form-control" placeholder="None"/></div>';
                else
                    displayHtml += '<input id="parcelReportedAreaInput" name="parcelreportedarea" type="text" class="form-control" placeholder="None"/></div>';
                

                $(this).html(displayHtml);
                $(this).show(300);

                $('#parcelReportedAreaInput').on('focus', function(event){
                    $('#parcelReportedAreaWarn').trigger('display');
                })
            }
            else
            {
                $(this).trigger('disappear');

            }
        });
        
        // @Event
        // Name: Display
        // DOM ELEMENT/ID: DIV/tierOneRow
        // Purpose: Displays the add button for entering in tier one data
        $('#tierOneRow').on('display', function(event, parcel){
            var displayHtml = '<div class="col-sm-3 col-sm-offset-9">' +
                '<button type="button" data-target="#t1Modal" data-toggle="modal" class="btn btn-primary btn-sm">Add</button></div>';
            $(this).html(displayHtml);
            
              var url = '/api/v1/parcel-carbon/' + parcel  + '/';
              $.get(url, function(data1, status){
                  dataSet =data1;
               });             
              
        });
        
        // @Event
        // Name: Display
        // DOM ELEMENT/ID: DIV/tierTwoRow
        // Purpose: Displays the add button for entering in tier two data
        $('#tierTwoRow').on('display', function(event, parcel){
            var displayHtml = '<div class="col-sm-3 col-sm-offset-9">' +
                '<button type="button" data-target="#t2Modal" data-toggle="modal" class="btn btn-primary btn-sm">Add</button></div>';
            $(this).html(displayHtml);            
             var url = '/api/v1/parcel-carbon/' + parcel  + '/';
              $.get(url, function(data1, status){
                  dataSet =data1;
               });             
               
             
        });
        $('#plotInformation').on('display', function(event, parcel){
            $(this).empty();
            $.ajax({
                url: '/api/v1/plot/?limit=50&parcel=' + parcel,
                type: 'GET',
                dataType: 'json',
                beforeSend: function() { $(".overlay").fadeIn(); },
                complete: function(){ $(".overlay").fadeOut(); }, 
                success: function(data){
                    var div = $('<div class="col-sm-9" />');
                    var plotSelect = $('<select id="plotDropdown" name="plotDropdown" class="form-control" />');
                    plotSelect.appendTo(div);
                    $('<option />', {value:'', text: 'Select a plot'}).appendTo(plotSelect);;
                    
                    if ( data['objects'].length > 0 )
                    {
                        console.log('in here');
                        $.each( data['objects'], function(v, s){
                            $('<option />', {value:s['id'], text: s['name']}).appendTo(plotSelect);
                        });
                        
                    }
                    $('#plotInformation').append(div);
                    $('#plotInformation').append('<div class="col-sm-3"><button type="button" data-target="#addPlot" data-toggle="modal" class="btn btn-primary btn-sm">Add Plot</button><button type="button" id="plotDetailsButton" data-target="#plotDetailsModal" data-toggle="modal" class="btn btn-success btn-sm" style="margin-left:5px;">Details</button></div>');
                    

                    // when the selected plot is changed
                    plotSelect.on('change', function(event){
                        plotid = $(this).val()

                        if (plotid != '')
                        {
                            $('#plotImageLink').html('<a href="/measuring/image_management/' + projectID + '/' + plotid + '/" class="btn btn-primary btn-sm">View Images</a>');
                            $.ajax({
                                url: '/api/v1/plot/' + plotid + '/',
                                type: 'GET',
                                dataType: 'json',
                                success: function(data){
                                    var shape = "None";
                                    var dimensions = "0";
                                    var root_shoot = data["root_shoot_ratio"];

                                    if(data['shape_reported'] != null)
                                        shape = data['shape_reported'];
                                    if(data['dimensions_reported'] != null)
                                        dimensions = data['dimensions_reported'];

                                    console.log("shape: " + shape + "\ndimensions: " + dimensions);

                                    if(shape == "circle")
                                    {
                                        $("#circleShapeEdit").click();
                                        $("#editRadius").val(dimensions);
                                        $("#edit_xdimension").val(0);
                                        $("#edit_ydimension").val(0);
                                    }
                                    else
                                    {
                                        var dimXY = dimensions.split("x");
                                        $("#rectangleShapeEdit").click();
                                        $("#edit_xdimension").val(dimXY[0]);
                                        $("#edit_ydimension").val(dimXY[1]);
                                        $("#editRadius").val(0);
                                    }

                                    $("#plotReportedAreaInput").val(dimensions);
                                    $('#editRootShoot').val(root_shoot);
                                    $("#plotData").show(300);

                                    var trees = data['trees'];

                                    var treeSpecies = new Array();

                                    for(var i=0; i < trees.length; i++)
                                    {
                                        $.ajax({
                                            url: trees[i],
                                            type: 'GET',
                                            dataType: 'json',
                                            success: function(tree_data) {
                                                // check if species & genus combination is already used, otherwise, add it.
                                                var flag = true;

                                                for(var j=0; j < treeSpecies.length; j++)
                                                {
                                                    if(treeSpecies[j][0] == tree_data['species'] && treeSpecies[j][1] == tree_data['genus'])
                                                    {
                                                        flag = false;                                             
                                                    }
                                                }

                                                if(flag)
                                                {
                                                    treeSpecies.push(new Array(tree_data['species'], tree_data['genus']));   
                                                }
                                            }
                                        });
                                    }

                                    $.ajax({
                                        url: '/api/v1/plot-carbon/' + plotid + '/',
                                        type: 'GET',
                                        dataType: 'json',
                                        success: function(carbon_stocks){

                                            var treeCount = carbon_stocks['estimated_n_trees'];

                                            var speciesCount = treeSpecies.length;


                                            var agb = carbon_stocks['agb_tc_ha'];
                                            var bgb = carbon_stocks['bgb_tc_ha'];
                                            var soc = carbon_stocks['soc_tc_ha'];
                                            var litter = carbon_stocks['litter_tc_ha'];
                                            var deadwood = carbon_stocks['deadwood_tc_ha'];

                                            if(agb == null)
                                                agb = "--";
                                            else
                                                agb = numberWithCommas(parseFloat(agb).toFixed(4));

                                            if(bgb == null)
                                                bgb = "--";
                                            else
                                                bgb = numberWithCommas(parseFloat(bgb).toFixed(4));

                                            if(soc == null)
                                                soc = "--";
                                            else
                                                soc = numberWithCommas(parseFloat(soc).toFixed(4));

                                            if(litter == null)
                                                litter = "--";
                                            else 
                                                litter = numberWithCommas(parseFloat(litter).toFixed(4));

                                            if(deadwood == null)
                                                deadwood = "--";
                                            else
                                                deadwood = numberWithCommas(parseFloat(deadwood).toFixed(4));

                                            if(treeCount == null)
                                                treeCount = 0;
                                            

                                            $("#soilInv").html(soc);
                                            $("#litterInv").html(litter);
                                            $("#agbInv").html(agb);
                                            $("#bgbInv").html(bgb);
                                            $("#deadwoodInv").html(deadwood);
                                            $("#aeqInv").html(carbon_stocks['allometric_equation']);
                                            $("#treesInv").html(treeCount);
                                            $("#speciesInv").html(speciesCount);
                                            $("#plotDetailsPage").html("<a href=\"/measuring/data_management/plot_inventory/" + projectID + "/" + plotid + "/\">Plot Inventory</a>");
                                        }
                                    });


                                    $("#plotDetailsButton").show(300);
                                    $('#plotImageViewer').show(300);

                                }
                            });
                        }
                        else
                        {
                            $("#plotData").hide(300);
                            $("#plotDetailsButton").hide(300);
                            $('#plotImageViewer').hide(300);
                        }
                    });
                    plotSelect.change();
                },
            });
        });
        
        // @Event
        // Name: Disappear
        // DOM ELEMENT/ID: DIV/reportedAreaDirections
        // Purpose: Remove the html from the reported directions and hide that div tag
        $('#reportedAreaDirections').on('disappear', function(event){
            $(this).hide(300);
            $(this).empty();
        });

        // @Event
        // Name: Disappear
        // DOM ELEMENT/ID: DIV/parcelInformation
        // Purpose: Remove the html from the parcel information and hide that div tag
        $('#parcelInformation').on('disappear', function(event){
            $(this).hide(300);
            $(this).empty();

            $('#parcelReportedAreaWarn').trigger('disappear');
            $('#tierOneRow').trigger('disappear');
            $('#tierTwoRow').trigger('disappear');
            $('#plotInformation').trigger('disappear');
        });
        
        // @Event
        // Name: Disappear
        // DOM ELEMENT/ID: DIV/parcelReportedAreaWarn
        // Purpose: Remove the html and hide that div tag
        $('#parcelReportedAreaWarn').on('disappear', function(event){
            $(this).hide(300);
            $(this).empty();
        });

        // @Event
        // Name: Disappear
        // DOM ELEMENT/ID: DIV/tierOneRow
        // Purpose: Restore the warning that the user must select a parcel
        $('#tierOneRow').on('disappear', function(event){
            var displayHtml = '<div class="col-sm-9"><em>You must select a parcel before you can submit tier one data.</em></div>';

            $(this).html(displayHtml);
        })

        // @Event
        // Name: Disappear
        // DOM ELEMENT/ID: DIV/tierTwoRow
        // Purpose: Restore the warning that the user must select a parcel
        $('#tierTwoRow').on('disappear', function(event){
            var displayHtml = '<div class="col-sm-9"><em>You must select a parcel before you can submit tier two data.</em></div>';

            $(this).html(displayHtml);
        })

        $('#plotInformation').on('disappear', function(event){
            $(this).hide(300);
            $(this).html('<div class="col-sm-9"><em>You must select a parcel before you can select a plot.</em></div>');
            $(this).show(300);
        });

        
        //
        //************************************************************************
        //          Handle the process of setting the reported area
        //          of a project. All of the following event handlers
        //          are related to the reported area field/form
        //
        $('#reported_area_project').on('focus', function(event){
            $('#reportedAreaDirections').trigger('display');
            reportedArea = parseFloat($('#reported_area_project').val());
        });


        $('#reported_area_form').on('submit', function(event){
            event.preventDefault();

            var temp = parseFloat($('#reported_area_project').val()).toFixed(2);
            
            if(isNaN(temp))
            {
                notValid('Project Reported Area');
                $(this)[0].reset();
            }
            else
            {
                
                $('#reported_area_project').val(temp);
                var request = new XMLHttpRequest();
                request.open('POST', '/measuring/parcel_management/edit_project_area/' + projectID + '/', false);
                request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
               request.send($(this).serialize());

                if (request.status === 200 )
                {
                    reportedArea = temp;
                    $('#ajaxMessages').empty();
                    $('#reportedAreaDirections').trigger('disappear');
                }
                else
                {
                    notValid('Project Reported Area')
                    $(this)[0].reset();
                }

                 
             }
        })
            
        //
        //***********************************************************************
        //
        //***********************************************************************
        //
        $('#parcelDropdown').on('change', function(event){
            parcelid = $(this).val();
            $('#parcelInformation').trigger('disappear');
            parcelChanged();
        });

        function parcelChanged()
        {
            if (parcelid != '')
            {
                $.ajax({
                    url: '/api/v1/parcel/' + parcelid + '/',
                    type: 'GET',
                    dataType: 'json',
                    success: function(data){
                        var mapped = '0.0 ha';
                        var rep = '';

                        if (data['area_mapped'] != null)
                            mapped = data['area_mapped'] + ' ha';
                        if (data['area_reported'] != null)
                            rep = data['area_reported'];

                        $('#parcelInformation').trigger('display', [parcelid, mapped, rep]);
                        $('#tierOneRow').trigger('display', [parcelid]);
                        $('#tierTwoRow').trigger('display', [parcelid]);
                        
                        $('#plotInformation').trigger('display', [parcelid]);

                    }
                })
            }
            else
            {
                $("#plotData").hide(300);
            }            
        }



        $('#parcelReportedForm').on('submit', function(event){
            event.preventDefault();

            var temp = parseFloat($('#parcelReportedAreaInput').val()).toFixed(2);
            if(isNaN(temp))
            {
                notValid('Parcel Reported Area');
                $(this)[0].reset();
            }
            else
            {
                console.log($(this).serialize());
                var httprequest = new XMLHttpRequest();
                httprequest.open('POST', '/measuring/parcel_management/edit_parcel_area/' + parcelid + '/', false);
                httprequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                httprequest.send($(this).serialize());

                if(httprequest.status === 200)
                {
                    parcelReportedArea = temp;
                    $('#ajaxMessages').empty();
                    $('#parcelReportedAreaWarn').trigger('disappear');
                }
                else
                {
                    notValid('Parcel Reported Area');
                    $(this).reset();
                }
            }

        });

        

        //
        //**********************************************************************
        //
        //**********************************************************************
        //              Add a parcel to the project
        $('#addParcelForm').on('submit', function(event){
            event.preventDefault();
            console.log($('#addParcelName').val());
            var valid = false;
            
            // Store some variables so I don't keep referencing
            // them with jquery
            var parcelName = $('#addParcelName');
            var parcelArea = $('#addParcelArea');
            var parcelDD = $('#parcelDropdown');
            if(!parcelName.val()){
                parcelName.css({"border-color" : "red", "box-shadow" : "0 0 5px red", "transition" : "box-shadow linear 1s", "-webkit-transition":"box-shadow linear 1s"});
            }
            else{
                parcelName.removeAttr("style");
            }

            if(!parcelArea.val()){
               parcelArea.css({"border-color" : "red", "box-shadow" : "0 0 5px red", "transition" : "box-shadow linear 1s", "-webkit-transition":"box-shadow linear 1s"});
            }
            else if ( isNaN($('#addParcelArea').val())){
                parcelArea.css({"border-color" : "red", "box-shadow" : "0 0 5px red", "transition" : "box-shadow linear 1s", "-webkit-transition":"box-shadow linear 1s"});
            }
            else{
                valid = true;
                parcelArea.removeAttr("style");
            }

            if ( valid == true ){
                console.log($(this).serialize());

                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/measuring/parcel_management/add_parcel/' + projectID + '/', false);
                xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xhr.send($(this).serialize());

                if( xhr.status === 200 ){
                    var temp = xhr.responseText.split(',');
                    var s = $("<option />", {value: temp[1], text: temp[0]}).attr("selected", "selected");
                    parcelDD.append(s);
                    $(this)[0].reset();
                    $('#addParcel').modal('hide');
                    parcelDD.trigger("change");

                }
            }

        });

        $('#addPlotForm').on('submit', function(event){
            event.preventDefault();
            console.log("In plot form");
            var plotShape = $("input[type=radio][name=shape]:checked").val();
            var name = $('#addPlotName').val();
            var dimension;
            switch(plotShape)
            {
                case 'rectangle':
                    dimension = $('#xdimension').val() + 'x' + $('#ydimension').val();
                    break;
                case 'circle':
                    dimension = $('#radius').val();
                    break;
            }

            var area = parseFloat($('#plotReportedArea').text());

            if ( !name || name == '' ){
                console.log("in this if statement");
                $('#addPlotName').css({"border-color":"red", "box-shadow":"0 0 5px red", "transition": "box-shadow linear 1s"});
            }
            else
            {
                var d = {
                    "name" : name,
                    "area_reported" : area,
                    "shape_reported" : plotShape,
                    "dimensions_reported" : dimension,
                    "parcel" : "/api/v1/parcel-with-hidden-no-plots/" + parcelid +"/",
                }

                var csrftoken = getCookie('csrftoken');
                var httprequest = new XMLHttpRequest();
                httprequest.open('POST', '/api/v1/plot/', false);
                httprequest.setRequestHeader('Content-type', 'application/json');
                httprequest.setRequestHeader('X-CSRFToken', csrftoken);
                httprequest.send(JSON.stringify(d));

                if ( httprequest.status === 201 )
                {
                    $('#plotInformation').trigger('display', [parcelid]);
                    $('#addPlot').modal('hide');
                }

            }         
            

        })

        $("#plotInfoForm").on("submit", function(event) {
            event.preventDefault();

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/measuring/parcel_management/edit_plot_info/' + plotid + '/', false);
            xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhr.send($(this).serialize());

            if(xhr.status === 200)
            {
                $("#plotData").hide(300);
                $("#plotData").show(300);
            }
        })
        //
        // Submit the form for the tier 1 values
        //
        $('#t1Modal').on('shown.bs.modal', function(event){
            $('#t1form').on('submit', function(event){
                    event.preventDefault();     // Prevent the default form submit action
                    var d = {};                 // Create the dictionary to store our data
                    var parcel = $('#parcelDropdown').val();
                    console.log(parcel);

                    var csrftoken = getCookie("csrftoken");
                    // Fill the dictionary with the values that we need to submit
                    d = {
                        "t1_agb" : parseFloat($('#t1_agb').val()),
                        "t1_bgb" : parseFloat($('#t1_bgb').val()),
                        "t1_soc" : parseFloat($('#t1_soc').val()),
                        "t1_deadwood" : parseFloat($('#t1_deadwood').val()),
                        "t1_litter" : parseFloat($('#t1_litter').val()),
                    };

                    // This is our ajax call. Working with jquery it wouldn't work
                    var request = new XMLHttpRequest();
                    request.open('PATCH', '/api/v1/parcel/' + parcel + '/', false);
                    request.setRequestHeader("Content-type", "application/json");
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                    request.send(JSON.stringify(d));

                    // Handle a response code of 202, which means the patch has
                    // be accepted
                    if(request.status === 202)
                    {
                        $('#t1Modal').modal('hide');
                    }
                    
                });  
               	  
		  var modal = $(this);		 
		  modal.find('.modal-body #t1_agb').val( dataSet.t1_agb);
                  modal.find('.modal-body #t1_bgb').val(dataSet.t1_bgb);
		  modal.find('.modal-body #t1_soc').val(dataSet.t1_soc );
		  modal.find('.modal-body #t1_deadwood').val(dataSet.t1_deadwood );
		  modal.find('.modal-body #t1_litter').val(dataSet.t1_litter);	          
        });
    
        // 
        // Submit the form for the tier 2 values
        //
        $('#t2Modal').on('shown.bs.modal', function(event){

            $('#t2form').on('submit', function(event){
                    event.preventDefault();
                    var d = {};
                    var parcel = $('#parcelDropdown').val();
                    d = {
                        "t2_agb" : parseFloat($('#t2_agb').val()),
                        "t2_bgb" : parseFloat($('#t2_bgb').val()),
                        "t2_soc" : parseFloat($('#t2_soc').val()),
                        "t2_deadwood" : parseFloat($('#t2_deadwood').val()),
                        "t2_litter" : parseFloat($('#t2_litter').val()),
                    };

                    // This is our ajax call. Working with jquery it wouldn't work

                    var csrftoken = getCookie("csrftoken");
                    var request = new XMLHttpRequest();
                    request.open('PATCH', '/api/v1/parcel/' + parcel + '/', false);
                    request.setRequestHeader("Content-type", "application/json");
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                    request.send(JSON.stringify(d));

                    if(request.status === 202)
                    {
                        $('#t2Modal').modal('hide');
                    }
                    
                });
                  var modal = $(this);		 
		  modal.find('.modal-body #t2_agb').val( dataSet.t2_agb);
                  modal.find('.modal-body #t2_bgb').val(dataSet.t2_bgb);
		  modal.find('.modal-body #t2_soc').val(dataSet.t2_soc );
		  modal.find('.modal-body #t2_deadwood').val(dataSet.t2_deadwood );
		  modal.find('.modal-body #t2_litter').val(dataSet.t2_litter);	
        });


        $('input[name=shapeEdit]:radio').change(function(event){
            if($('#circleShapeEdit').is(':checked'))
            {
                $('#editDimensionsLabel').text('Radius (m): ');
                $("#editRectDim").hide(300);
                $("#editRadius").show(300);     
            }
            else
            {
                $('#editDimensionsLabel').text('Dimensions (m^2): ');
                $("#editRadius").hide(300);
                $("#editRectDim").show(300);
            }
        })

        // format so numbers use commas every 3 places over.
        function numberWithCommas(x) {
            var parts = x.toString().split(".");
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            return parts.join(".");
        }

        // End document ready()        
    })
    $('#t1Modal').on('hidden.bs.modal', function(event){
        //$('#t1form')[0].reset();
    })
    $('#t2Modal').on('hidden.bs.modal', function(event){
        //$('#t2form')[0].reset();
    })
