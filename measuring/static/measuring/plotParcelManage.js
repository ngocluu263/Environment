
        plot_ids = new Array();
        $(document).ready(function(){
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
                            var plot_parcel_id = plot["plot__parcel__id"];
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
                            var newRow = "<tr id='plotRow" + plot["id"] + "' data-parcel-id='" + plot_parcel_id + "'><td class='col-sm-3'>" + plot["name"] + 
                                "</td><td class='col-sm-3'>" + "<select id='plotChangeParcel" + plot["id"] + "' class='form-control plotChangeParcel'>" +
                                "<option value='{{ hiddenparcel.id }}'>{{ hiddenparcel.name }}</option>";
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
                                    newRow += '<input type="checkbox" disabled /> Litter '

                                if(plot["has_deadwood_data"])
                                    newRow += '<input type="checkbox" checked="checked" disabled/> Deadwood ';
                                else
                                    newRow += '<input type="checkbox" disabled /> Deadwood ';


                                newRow += "</td><td class='col-sm-3'>" + 
                                "<select id='plotAeqSelect" + plot["id"] + "' class='form-control plotAeqSelect'>";
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



        $("#selectToDeletePlots").click( function() {
            if ($(this).text() == "Select All")
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
                $(this).text("Select All");
                $(this).attr('class', 'btn btn-info btn-sm');
            };
        });



        $("#selectToDeleteParcels").click( function() {
            if ($(this).text() == "Select All")
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
                $(this).text("Select All");
                $(this).attr('class', 'btn btn-info btn-sm');
            };
        });


        $("#managePlotsParcel").on('submit', function(event) {
            event.preventDefault();
            $('.overlay').fadeIn();
            savePlots();
            saveParcels();
            saveProject();
            $('.overlay').fadeOut();
            //window.location.reload();

        });

        function hidePlotsFromParcel(parcel_id) {
            $.ajax({
                url: '/api/v1/plot/?parcel=' + parcel_id,
                type: 'GET',
                dataType: 'json',
                success: function(data) {
                    $.each(data["objects"], function(v, plot) {
                        $("#plotRow" + plot["id"]).hide(300);
                    });
                }
            })
        }

        function deletePlot(plot_id){
            $.ajax({
                url: '/api/v1/plot/' + plot_id + '/',
                type: 'DELETE',
                dataType: 'json',
                success: function(data) {
                    $("#plotRow" + plot_id).hide(300);
                }
            });       
        }

        function deleteParcel(parcel_id) {
            hidePlotsFromParcel(parcel_id);   
             $.ajax({
                url: '/api/v1/parcel/' + parcel_id + '/',
                type: 'DELETE',
                dataType: 'json',
                success: function(data) {
                    $("#" + parcel_id).hide(300);
                }
            });


        }


        function applyPlotChanges(plot_id, changedData)
        {
            var request = new XMLHttpRequest();
            request.open('PATCH', '/api/v1/plot/' + plot_id + '/', false);
            request.setRequestHeader('Content-type', 'application/json');
            request.send(JSON.stringify(changedData));

            if(request.status == 202)
            {
                var plotRow = $("#plotRow" + plot_id);
                plotRow.hide(300);
                plotRow.show(300);
            }
        }

        function applyParcelChanges(parcel_id, changedData)
        {
            var request = new XMLHttpRequest();
            request.open('PATCH', '/api/v1/parcel/' + parcel_id + '/', false);
            request.setRequestHeader('Content-type', 'application/json');
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
                parcelRow.hide(300);
                parcelRow.show(300);
            }           
        }

        function applyProjectChanges(changedData)
        {
            var request = new XMLHttpRequest();
            request.open('PATCH', '/api/v1/project/{{ project.id }}/', false);
            request.setRequestHeader('Content-type', 'application/json');
            request.send(JSON.stringify(changedData));

            if(request.status === 204)
            {

            }
        }



        function savePlots() {
            for(var i=0; i < plot_ids.length; i++)
            {
                if($("#deletePlot" + plot_ids[i]).prop('checked'))
                {
                    deletePlot(plot_ids[i]);
                }
                else 
                {
                    var changedData = {};
                    var oChangeParcel = $("#plotChangeParcel" + plot_ids[i]);
                    var oChangeAeq = $("#plotAeqSelect" + plot_ids[i]);

                    if(oChangeParcel.prop("dirty"))
                    {
                        if(oChangeParcel.val() == '' || !oChangeParcel.val())
                            changedData["parcel"] = null
                        else
                            changedData["parcel"] = "/api/v1/parcel-with-hidden-no-plots/" + oChangeParcel.val() + "/";
                        oChangeParcel.prop("dirty", false);
                    }

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
                    
                    if(JSON.stringify(changedData) != "{}")
                    {
                        console.log("changed data: " + JSON.stringify(changedData));
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
                else 
                {
                    var changedData = {}
                    var oRename = $("#renameParcel{{ parcel.id }}");
                    var oChangeAeq = $("#parcelAeqSelect{{ parcel.id }}");

                    if(oRename.val() != '' && oRename.prop("dirty"))
                    {
                        changedData["name"] = oRename.val();
                        oRename.prop("dirty", false);
                    }

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