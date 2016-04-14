plot_ids = new Array();
    $(document).ready(function(){
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
            var plotHtml = '';
            $.ajax({
                type: 'GET',
                url: '/api/v1/plot/?parcel__project={{ project.id }}',
                dataType: 'json',
                async: false,
                success: function(data) {
                    $.each(data["objects"], function(v, plot){
                        plot_ids.push(plot["id"])
                        var aeq_url = plot["aeq"];
                        var aeq = 0;
                        if(aeq_url != null)
                        {
                            $.ajax({
                                type: 'GET',
                                url: aeq_url,
                                dataType: 'json',
                                async: false,
                                success: function(aeqData) {
                                    aeq = aeqData['id'];
                                }
                            });
                        }
                        console.log(plot);
                        // Create a new row for us to append
                        var newRow = "<tr id='plotRow" + plot["id"] + "'><td class='col-sm-3'>" + plot["name"] + 
                            "</td><td class='col-sm-3'>" + "<select id='plotChangeParcel" + plot["id"] + "' class='form-control plotChangeParcel'>" + 
                            "<option value='' disabled>-- No Parcel --</option>"; 
                            // make the current parcel the starting selected one
                            {% for parc in parcels %}
                                if({{ parc.id }} == plot["parcel__id"]) {
                                    newRow = newRow + "<option value='{{ parc.id }}' selected='selected'>{{ parc.name }}</option>"   
                                }
                                else
                                {
                                    newRow += "<option value='{{ parc.id }}'>{{ parc.name }}</option>"
                                }
                            {% endfor %}
                            newRow += "</select>" + 
                            //"</td><td class='col-sm-4'>" + "<input type='text' id='renamePlot" + plot["id"] + "' name='renamePlot" + plot["id"] + "' class='form-control' />" + 
                            "</td><td class='col-sm-3'>";
                            
                            console.log(plot["has_biomass_data"]);

                            if(plot["has_biomass_data"])
                                newRow += '<input type="checkbox" checked="checked" disabled/> Biomass ';
                            else
                                newRow += '<input type="checkbox" disabled /> Biomass ';

                            if(plot["has_soil_data"])
                                newRow += '<input type="checkbox" checked="checked" disabled/> Soil ';
                            else
                                newRow += '<input type="checkbox" disabled /> Soil ';
                            newRow += '<br />';
                            if(plot["has_litter_data"])
                                newRow += '<input type="checkbox" checked="checked" disabled/> Litter ';
                            else
                                newRow += '<input type="checkbox disabled/> Litter '

                            if(plot["has_deadwood_data"])
                                newRow += '<input type="checkbox" checked="checked" disabled/> Deadwood ';
                            else
                                newRow += '<input type="checkbox" disabled/> Deadwood ';

                            // add aeq selected next
                            newRow += "</td><td class='col-sm-3'>" + 
                            "<select id='plotAeqSelect" + plot["id"] + "' class='form-control plotAeqSelect'>" +
                            "<option id='' disabled>Select an AEQ</option>";
                            if(aeq == 0)
                            {
                               newRow += "<option id='0' selected='selected'>-- Inherited from Parcel --</option>"; 
                            }
                            else
                            {
                                newRow += "<option id='0' >-- Inherited from Parcel --</option>"; 
                            }
                            
                            {% for eq in equations %}
                                if({{ eq.id }} == aeq)
                                {
                                    newRow += "<option id='plotEq{{ eq.id }}' value='{{ eq.id }}' selected='selected'>{{ eq.name }}</option>";
                                }
                                else
                                {
                                    newRow += "<option id='plotEq{{ eq.id }}' value='{{ eq.id }}'>{{ eq.name }}</option>";
                                }
                                
                            {% endfor %}
                            newRow += "</select>" + 
                            "</td><td class-'col-sm-1'>" + "<input type='checkbox' name='deletePlot" + plot["id"] + "' id='deletePlot" + plot["id"] + "' />" + "</td></tr>";

                        plotHtml += newRow;



                    });

                    $('#plotsTbody').append(plotHtml);
                }
            });

            $(".plotAeqSelect").change(function() {
                $(this).prop("dirty", true);
            });
            
            $(".plotChangeParcel").change(function() {
                $(this).prop("dirty", true);
            });

            $(".parcelAeqSelect").change(function() {
                $(this).prop("dirty", true);
            });

            $(".renameParcel").change(function() {
                $(this).prop("dirty", true);
            });

            $("#projectAeqSelect").change(function() {
                $(this).prop("dirty", true);
            });

    });



    $("#deletePlots").click( function() {
        if ($(this).text() == "Delete All")
        {
            for(var i=0; i < plot_ids.length; i++)    
            {
            $("#deletePlot" + plot_ids[i]).prop('checked', true);
            }
            $(this).text("Uncheck All");
            $(this).attr('class', 'btn btn-primary btn-sm');
        }
        else
        {
            for(var i=0; i < plot_ids.length; i++)    
            {
            $("#deletePlot" + plot_ids[i]).prop('checked', false);
            }
            $(this).text("Delete All");
            $(this).attr('class', 'btn btn-danger btn-sm');
        };
    });

    $("#deleteParcels").click( function() {
        if ($(this).text() == "Delete All")
        {
            {% for parcel in parcels %}
                $("#deleteParcel{{ parcel.id }}").prop('checked', true);
            {% endfor %}
            $(this).text("Uncheck All");
            $(this).attr('class', 'btn btn-primary btn-sm');
        }
        else
        {
            {% for parcel in parcels %}
                $("#deleteParcel{{ parcel.id }}").prop('checked', false);
            {% endfor %}
            $(this).text("Delete All");
            $(this).attr('class', 'btn btn-danger btn-sm');
        };
    });

    $("#managePlotsParcel").on('submit', function(event) {
        event.preventDefault();

        // saves plots before parcels, in case any plots are deleted from deleting parcels
        savePlots();
        saveParcels();
        saveProject();

        //window.location.reload();

    });

    function hidePlotsFromParcel(parcel_id) {
        $.ajax({
            url: '/api/v1/plot/?parcel=' + parcel_id,
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                $.each(data["objects"], function(v, plot) {
                    $("#plotRow" + plot["id"]).hide(200);
                });
            }
        })
    }

    function deletePlot(plot_id){
        $.ajax({
            url: '/api/v1/plot/' + plot_id + '/',
            type: 'DELETE',
            dataType: 'json',
            beforeSend: function(xhr, settings){
                var csrftoken = getCookie('csrftoken');
                if ( !csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function(data) {
                $("#plotRow" + plot_id).hide(200);
            }
        });       
    }

    function deleteParcel(parcel_id) {
        hidePlotsFromParcel(parcel_id);   
         $.ajax({
            url: '/api/v1/parcel/' + parcel_id + '/',
            type: 'DELETE',
            dataType: 'json',
            beforeSend: function(xhr, settings){
                console.log('here');
                var csrftoken = getCookie('csrftoken');
                if ( !csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function(data) {
                $("#" + parcel_id).hide(200);
            }
        });        

    }


    // apply all changes to plot that have been done
    function applyPlotChanges(plot_id, changedData)
    {
        var request = new XMLHttpRequest();
        var csrftoken = getCookie('csrftoken');
        request.open('PATCH', '/api/v1/plot/' + plot_id + '/', false);
        request.setRequestHeader('Content-type', 'application/json');
        request.setRequestHeader('X-CSRFToken', csrftoken);
        request.send(JSON.stringify(changedData));

        if(request.status == 202)
        {
            var plotRow = $("#plotRow" + plot_id);
            plotRow.hide(200);
            plotRow.show(200);            
        }
    }

    // apply all changes that have benn done to a parcel
    function applyParcelChanges(parcel_id, changedData)
    {
        var request = new XMLHttpRequest();
        var csrftoken = getCookie('csrftoken');
        request.open('PATCH', '/api/v1/parcel/' + parcel_id + '/', false);
        request.setRequestHeader('Content-type', 'application/json');
        request.setRequestHeader('X-CSRFToken', csrftoken);
        request.send(JSON.stringify(changedData));

        if(request.status === 202)
        {
            var parcelRow = $("#" + parcel_id);
            parcelRow.hide();
            if(changedData["name"] != null)
            {
                var oName = $('#' + parcel_id + '_name');
                var oRename = $("#renameParcel" + parcel_id);
                oName.text(changedData["name"]);
                oRename.val("");
                $(".plotChangeParcel option").each(function () {
                    if($(this).val() == parcel_id)
                    {
                        $(this).html(changedData["name"]);
                    }
                });
            }
                
            parcelRow.show(300);            
        }           
    }

    // apply changes to project
    function applyProjectChanges(changedData)
    {
        var request = new XMLHttpRequest();
        var csrftoken = getCookie('csrftoken');
        request.open('PUT', '/api/v1/project/{{ project.id }}/', false);
        request.setRequestHeader('Content-type', 'application/json');
        request.setRequestHeader('X-CSRFToken', csrftoken);
        request.send(JSON.stringify(changedData));

        if(request.status === 204)
        {
          
        }
        else{           
        }
    }



    function savePlots() {

        for(var i=0; i < plot_ids.length; i++)
        {
            if($("#deletePlot" + plot_ids[i]).prop('checked'))
            {
                deletePlot(plot_ids[i]);
            }
            else // only apply changes if plot isn't being deleted
            {
                var changedData = {};
                var oChangeParcel = $("#plotChangeParcel" + plot_ids[i]);
                var oChangeAeq = $("#plotAeqSelect" + plot_ids[i]);

                // if parcel it belongs to has changed.
                if(oChangeParcel.prop("dirty"))
                {
                    changedData["parcel"] = "/api/v1/parcel-with-hidden-no-plots/" + oChangeParcel.val() + "/";
                    oChangeParcel.prop("dirty", false);
                }

                // if aeq has changed
                if(oChangeAeq.prop("dirty"))
                {
                    if(oChangeAeq.val() > 0)
                    {
                        changedData["aeq"] = "/api/v1/aeq/" + oChangeAeq.val() + "/";                       
                    }
                    else
                    {
                        changedData["aeq"] = null;
                    }
                    oChangeAeq.prop("dirty", false);
                }


                // onlty do if there things have changed
                if(JSON.stringify(changedData) != "{}")
                {
                    console.log("changed data: " + JSON.stringify(changedData));
                    // applys all changes at once
                    applyPlotChanges(plot_ids[i], changedData);                    
                }
            }
        }
       
    }

    function saveParcels() {
        {% for parcel in parcels %}
            if($("#deleteParcel" + {{ parcel.id }}).prop('checked'))
            {
                deleteParcel({{ parcel.id }});
            }
            else // only apply changes if parcel isn't being deleted.
            {
                var changedData = {}
                var oRename = $("#renameParcel{{ parcel.id }}");
                var oChangeAeq = $("#parcelAeqSelect{{ parcel.id }}");

                // check if something in rename field
                if(oRename.val() != '' && oRename.prop("dirty"))
                {
                    changedData["name"] = oRename.val();
                    oRename.prop("dirty", false);
                }

                // check if aeq has been changed
                if(oChangeAeq.prop("dirty"))
                {
                    if(oChangeAeq.val() > 0)
                    {
                        changedData["aeq"] = "/api/v1/aeq/" + oChangeAeq.val() + "/";                       
                    }
                    else
                    {
                        changedData["aeq"] = null;
                    }
                    oChangeAeq.prop("dirty", false);
                }

                // do only if stuff has been changed
                if(JSON.stringify(changedData) != "{}")
                {
                    console.log("changed parcel data: " + JSON.stringify(changedData));
                    applyParcelChanges({{ parcel.id }}, changedData);
                }

            }               
        {% endfor %}        
    }

    function saveProject() {
        var changedData = {}        
        var oChangeAeq = $("#projectAeqSelect");

        if(oChangeAeq.prop("dirty"))
        {
            changedData["aeq"] = "/api/v1/aeq/" + oChangeAeq.val() + "/";           
            oChangeAeq.prop("dirty", false);
        }        
        
        if(JSON.stringify(changedData) != "{}")
        {
            console.log("changed project data: " + JSON.stringify(changedData));
            applyProjectChanges(changedData);             
        } 
           
             
    }
