var googleMap      = null;
var googleMapType  = google.maps.MapTypeId.HYBRID;
var drawingState   = null;
var selectedShape  = null;
var deleteOverlay  = false;
var googleMapPrint = false
var ReDrawing      = false;
var project_id     = null;

var googleMapStartLatLng = new google.maps.LatLng(0, 0);
var googleMapLatLng = null;
//var googleMapZoomLevel = 2;
//var googleMapsDZoomLevel = 2;


var shadowImageUrl = "images/leafmarkersmshad.png";
var crosshairsImage = "images/crosshairs.png";
var litIconUrl = "images/leafmarkersmorng.png";
var iconUrl = "images/leafmarkersmgrn.png";

var tooltip = null;
var tooltip_index = -1;
var tooltip_html = null;

var uploadCoordinateState = ''

var googleMapMarkers = [];
var googleMapIcons = [];

function setProjectId(id) {
    project_id = id;
}

/**
 * Calculates the center point between boundries
 * @param  {bounds} bounds
 * @return {google.maps.LatLng}
 */
function calcBoundsCenter(bounds) {
    ne = bounds.getNorthEast();
    sw = bounds.getSouthWest();
    centerLat = sw.lat() + ( ( ne.lat() - sw.lat()) / 2 );
    centerLng = sw.lng() + ( ( ne.lng() - sw.lng()) / 2 );
    return new google.maps.LatLng(centerLat, centerLng);
}

/**
 * Clear's the Selected Shape variable. Set that selected shape to not be editable.
 * @return {None}
 */
function clearSelection() {
    if(selectedShape) {
        selectedShape.setEditable(false);
        selectedShape = null;
    }
}

/**
 * Sets a polygon as the selected shape, set it to be editable.
 * @param {Polygon} itemPolygon
 */
function setSelection(itemPolygon) {
    selectedShape = itemPolygon;
    itemPolygon.setEditable(true);
}

function initMap(options) {
    if ( options == null ) {
        options = {
            loadCookies : true,
        };
    }

    // Set the options for displaying the google maps
    var mapOptions = {
        mapTypeId        : googleMapType,
        streetViewControl: false,
        zoom: 2,
        center: new google.maps.LatLng(-34.397, 150.644)

    };


    // Initialzie the google maps object
    googleMap = new google.maps.Map(document.getElementById("mapcanvas"), mapOptions);

    // Initialize the drawing manager
    drawingManager = new google.maps.drawing.DrawingManager({
        drawingControl: false,
        markerOptions: {
            icon: './images/grnball.png',
        },
        polygonOptions: {
            fillColor    : '#00FF00',
            fillOpacity  : .5,
            strokeWeight : 3,
            strokeColor  : 'green',
            strokeOpacity: 1,
            clickable    : true,
            zIndex       : 0,
            editable     : true
        }
    });


    drawingManager.setMap(googleMap);


    //getArgv(googleMap);
    //getSessionVars(googleMap);

    // default zoom and center values
    var zoom = 2;
    var center = new google.maps.LatLng(googleMapStartLatLng.lat(), googleMapStartLatLng.lng());

    // if there's a cookie then split it accordingly and change the default values
    if(checkCookieExists('Zoom_Center_' + project_id)) {
        var cookie = getCookie('Zoom_Center_' + project_id);
        var array = cookie.split(':');
        zoom = parseFloat(array[1].split('&')[0]);
        var points = array[2].split(', ');
        var x = parseFloat(points[0].substring(1, points[0].length));
        var y = parseFloat(points[1].substring(0, points[1].length-1));
        center = new google.maps.LatLng(x, y);
    }

    googleMap.setZoom(zoom);
    googleMap.setCenter(center);
    googleMap.setMapTypeId(googleMapType);


    // create the base icons for our markers
    var baseIcon = {
        url: null,
        size: new google.maps.Size(16, 16),
        anchor: new google.maps.Point(8, 8),
        shadow: shadowImageUrl
    }

    var crossIcon = {
        url: crosshairsImage,
        shadow: null,
        size: new google.maps.Size(19, 19),
        anchor: new google.maps.Point(10, 10)
    }

    var cross_markerOptions = {
        icon: crossIcon,
        draggable: false,
        clickable: false,
        position: new google.maps.LatLng(googleMapStartLatLng.lat(), googleMapStartLatLng.lng()),
        map: googleMap
    };



    /**
     * Creates the marker that will be placed on the map. Also wires up the event
     * listeners to the marker for mouseover, mouseout, and clicking
     * @param  {[type]} point   [description]
     * @param  {[type]} tooltip [description]
     * @param  {[type]} infomsg [description]
     * @param  {[type]} iconurl [description]
     * @return {marker}         The marker object
     */
    function createMapMarker( point, tooltip, infomsg, iconurl ) {
        var Icon = baseIcon;
        Icon.image = iconurl;

        markerOptions = { icon:Icon };
        var marker = new google.maps.Marker(point, markerOptions);

        google.maps.event.addListener(marker, "mouseover", function() {
            if (googleMapPrint)
                return;

            googleMapLatLng = market.getLatLng();
            marker.setImage(litIconUrl);
            openTooltip(marker, tooltip);
        });

        google.maps.event.addListener(marker, "mouseout", function() {
            if (googleMapPrint)
                return;

            tooltip.hide();
            marker.setImage(iconurl);
        });

        google.maps.event.addListener(marker, "click", function() {
            if (googleMapPrint)
                return;

            tooltip.hide();
            googleMapLatLng = marker.getLatLng();

            var pt = googleMap.fromLatLngToContainerPixel(googleMapLatLng);
            pt = new GPoint(pt.x, pt.y - 50);
            googleMapLatLng = googleMap.fromContainerPixelToLatLng(pt);

            googleMap.panTo(googleMapLatLng);

            openInfoBox(marker, infomsg);
        });

        return marker;
    }


    for ( var i = 0; i < googleMapMarkers.length; i++ ) {
        var mark = googleMapMarkers[i];
        var icn = creatmapMarker(mark['latlng'], mark['tooltip'], mark['infomsg'], iconUrl);

        icn.setMap(googleMap);
        googleMapIcons[googleMapIcons.length] = icn;

        if ( tooltip_index == i) {
            openToolTip(icn, tooltip_html);
        }
    }

    // Event Listener : Click
    // Attached To: {map object} googleMap
    // Handles the event of clicking anywhere on the map, not on an object
    // on the map.
    //
    // Clears the selected item on the map, if any is selected.
    google.maps.event.addListener(googleMap, "click", function(event) {
        clearSelection();
    });
/*
    // Event Listener : Zoom
    // Attached To: {map object} googleMap
    // Handles the event of zoom changing.
    //
    //
    google.maps.event.addListener(googleMap, "zoom_changed", function(event) {
        checkCookie('zoom', parseFloat(googleMap.getZoom()))
    });


    // Event Listener : Position
    // Attached To: {map object} googleMap
    // Handles the event of zoom changing.
    //
    //
    google.maps.event.addListener(googleMap, "position_changed", function(event) {
        checkCookie('zoom', googleMap.getZoom())

    });
*/

    // Event Listener : mapTypeChanged
    // Attached To: {map object} googleMap
    // Handles the event of a change in map type.
    //
    // Updates the color of the text depending on the selected map type.
    google.maps.event.addListener(googleMap, "maptypechanged", function(){
        mapTypeChanged(googleMap);
    });

    // Event Listener : mousemove
    // Attached To: {map object} googleMap
    // Handles the event of moving the mouse on the map.
    //
    // Unsure
    google.maps.event.addListener(googleMap, "mousemove", function(event){
        mapMouseMoved(event.latlng);
    });



    function redrawingHandler( container, overlay ) {
        if ( container.getCurrent().editMode_reported ) {
            drawingManager.setDrawingMode(null);
            container.getCurrent().reportedPolyObject = overlay;
            container.getCurrent().setEventListeners();
            drawState = drawStateType.NORMAL;
            closePolygon(container.getCurrent().reportedPolyObject);
        }
        else {
            container.getCurrent().polyObject = overlay;
            container.getCurrent().setEventListeners();
            container.getCurrent().updateMarker();
            drawState = drawStateType.NORMAL;
            closePolygon(container.getCurrent().polyObject);
        }
    }
    // Event Listener : overlaycomplete
    // Attached To: {drawing manager object} drawingManager
    // Handles the completed overlay event.
    //
    // Creates the project, parcel, or plot based on the current drawing
    // state.
    google.maps.event.addListener(drawingManager, "overlaycomplete", function(event){
        clearSelection();

        if (deleteOverlay && event.type === google.maps.drawing.OverlayType.POLYGON) {
            event.overlay.setMap(null);
            event.overlay = null;
            deleteOverlay = false;

            if(ReDrawing) {
                clickedObject.polyObject.setMap(googleMap);
                clickedObject.reportedPolyObject.setMap(googleMap);
            }
            return;
        }
        else if (deleteOverlay) {
            deleteOverlay = false;
        }
        if ( event.type === google.maps.drawing.OverlayType.POLYGON) {
            if(ReDrawing) {
                ReDrawing = false;
                switch ( drawState ) {
                case drawStateType.DRAWPROJECT:
                    redrawingHandler( projectContainer, event.overlay );
                    break;
                case drawStateType.DRAWPARCEL:
                    redrawingHandler( parcelContainer, event.overlay );
                    break;
                case drawStateType.DRAWPLOT:
                    redrawingHandler( plotContainer, event.overlay );
                }
            }
            else {
                switch( drawState ) {
                case drawStateType.DRAWPROJECT:
                    createProjectMapObject({
                        addoverlay: true,
                        isorphan: false,
                        polyObject: event,
                        save: true,
                        id: null
                    });
                    closePolygon( projectContainer.getCurrent().polyObject);
                    break;
                case drawStateType.DRAWPARCEL:
                    createParcelMapObject({
                        addoverlay: true,
                        isorphan: false,
                        polyObject: event,
                        save: true,
                        id: null
                    });
                    closePolygon( parcelContainer.getCurrent().polyObject);
                    break;
                case drawStateType.DRAWPLOT:
                    createPlotMapObject({
                        addoverlay: true,
                        isorphan: false,
                        polyObject: event,
                        save: true,
                        id: null
                    });
                    closePolygon( plotContainer.getCurrent().polyObject);
                }
            }
        }
        else if ( event.type === google.maps.drawing.OverlayType.MARKER ) {
            switch ( drawState ) {
            case drawStateType.PLANTPROJECT:
                createProjectMapObject({
                    addoverlay: true,
                    isorphan: false,
                    polyObject: event,
                    save: true,
                    id: null
                });
                break;
            case drawStateType.PLANTPARCEL:
                createParcelMapObject({
                    addoverlay: true,
                    isorphan: false,
                    polyObject: event,
                    save: true,
                    id: null
                });
                break;
            case drawStateType.PLANTPLOT:
                createPlotMapObject({
                    addoverlay: true,
                    isorphan: false,
                    polyObject: event,
                    save: true,
                    id: null
                });
            }
        }
    });

    google.maps.event.addListener(googleMap, "rightclick", function(event){
        if ( drawingManager.getDrawingMode() != null ) {
            deleteOverlay = true;
            drawingManager.setDrawingMode(null);
            drawState = drawStateType.NORMAL;
            google.maps.event.trigger(drawingManager, 'overlaycomplete', {type: 'none'});
        }
    });

    google.maps.event.addListener(googleMap, "zoom_changed", function(event){
        var cvalue = "Zoom:" + googleMap.zoom.toString() + "&Center:" + googleMap.center.toString();
        checkCookie("Zoom_Center_" + project_id, cvalue);
    });

    google.maps.event.addListener(googleMap, "center_changed", function(event){
        var cvalue = "Zoom:" + googleMap.zoom.toString() + "&Center:" + googleMap.center.toString();
        checkCookie("Zoom_Center_" + project_id, cvalue);
    });

    if ( options['loadCookies'])
        var setview = initSetView();
}

function getPolygonsFromDatabase() {
    var calls = [];
    calls.push(projectContainer.load());
    calls.push(parcelContainer.load());
    calls.push(plotContainer.load());
    $.when.apply($, calls);
}

function cancel() {
    google.maps.event.trigger(googleMap, "rightclick");
}

function reloadMap() {
    initMap();
    getPolygonsFromDatabase();
}

function insertPolyVertex( polyObject, vertex ) {
    var polyArray = polyObject.getPath();
    polyArray.push(vertex);
    polyObject.setpath(polyArray);
}


function drawPolygon(pType) {
    var polyOptions = null;
    deleteOverlay = false;
    ReDrawing = false;
    switch(pType) {
    case "project":
        drawState = drawStateType.DRAWPROJECT;
        polyOptions = {
            fillColor: '#00FF00',
            strokeColor: '#00FF00',
            zIndex: 0
        };
        break;
    case "parcel":
        drawState = drawStateType.DRAWPARCEL;
        polyOptions = {
            fillColor: '#0000FF',
            strokeColor: '#0000FF',
            zIndex: 0
        };
        break;
    }

    drawingManager.setOptions({
        drawingMode: google.maps.drawing.OverlayType.POLYGON,
        polygonOptions: polyOptions
    })
}

function placeMarker(pType) {
    var markOptions = null;
    deleteOverlay = false;
    ReDrawing = false;

    switch(pType) {
    case "project":
        drawState = drawStateType.PLANTPROJECT;
        markOptions = {
            icon: "/static/images/grnball.png"
        };
        break;
    case "parcel":
        drawState = drawStateType.PLANTPARCEL;
        markOptions = {
            icon: "/static/images/bluball.png"
        };
        break;
    case "plot":
        drawState = drawStateType.PLANTPLOT;
        markOptions = {
            icon: "/static/images/redball.png"
        };
        break;
    }
    drawingManager.setOptions({
        drawingMode: google.maps.drawing.OverlayType.MARKER,
        markerOptions: markOptions
    });
}

function enterCoordinates(pType) {
    var path = new google.maps.MVCArray();
    setCoordinateState(pType);

    if( enterCoordinateState != 2) {
        if ( $('#' + pType + 'CoordinateElements input').length/2 == 1 ) {
            return;
        }
        for ( var i = 1; i <= $('#' + pType + 'CoordinateElements input').length/2; i++) {
            var latID = "#"+pType+"_coord_"+i+"_lat";
            var lngID = "#"+pType+"_coord_"+i+"_lng";

            if ( $(latID).val() && $(lngID).val() ) {
                path.push(new google.maps.LatLng(parseFloat($(latID).val()), parseFloat($(lngID).val())));
            }
            else if ( !$(latID).val() && !$(lngID).val()) {
                break;
            }
            else if ( !$(latID).val() || !$(lngID).val()) {
                alert("You entered one coordinate. Expected pairs.");
                return;
            }

            if (enterCoordinateState == 2 && i == 4) {
                break;
            }
        }

        if ( path.getLength() == 0 ) {
            setCoordinateState('');
            return;
        }
    } else {
        path = [];
        for ( var i = 1; i <= $('#' + pType + 'CoordinateElements input').length/2; i++) {
            var latID = "#"+pType+"_coord_"+i+"_lat";
            var lngID = "#"+pType+"_coord_"+i+"_lng";

            if ( $(latID).val() && $(lngID).val() ) {
                var marker = new google.maps.Marker({
                    icon: "/static/images/redball.png"
                });
                marker.setPosition(new google.maps.LatLng(parseFloat($(latID).val()), parseFloat($(lngID).val())))
                path.push(marker);

            }
            else if ( !$(latID).val() && !$(lngID).val()) {
                break;
            }
            else if ( !$(latID).val() || !$(lngID).val()) {
                alert("You entered one coordinate. Expected pairs.");
                return;
            }

            if (enterCoordinateState == 2 && i == 4) {
                break;
            }
        }
    }

    if ( $('#enterCoordMapped').is(':checked') ) {
        switch (enterCoordinateState) {
        case 0:
            var projectPolygon = new google.maps.Polygon({
                fillColor: '#00FF00',
                strokeColor: '#00FF00',
                zIndex: 0,
            });
            projectPolygon.setPath(path);
            createProjectMapObject({
                addoverlay: true,
                isorphan: false,
                save: true,
                polyObject: {
                    type: google.maps.drawing.OverlayType.POLYGON,
                    overlay: projectPolygon
                }
            });
            break;
        case 1:
            var parcelPolygon = new google.maps.Polygon({
                fillColor: '#0000FF',
                strokeColor: '#0000FF',
                zIndex: 0,
                paths: path
            });
            createParcelMapObject({
                addoverlay: true,
                isorphan: false,
                save: true,
                polyObject: {
                    type: google.maps.drawing.OverlayType.POLYGON,
                    overlay: parcelPolygon
                }
            });
            break;
        case 2:
            for( var i in path ) {
                createPlotMapObject({
                    addoverlay: true,
                    isorphan: false,
                    save: true,
                    polyObject: {
                        type: google.maps.drawing.OverlayType.MARKER,
                        overlay: path[i]
                    }
                });
            }

            break;
        }
    } else {
        switch (enterCoordinateState) {
        case 0:
            var projectPolygon = new google.maps.Polygon({
                strokeColor: "#00AA00",
                strokeWeight: 2,
                strokeOpacity: 1.0,
                fillColor: "#FFE400",
                fillOpacity: 0.25,
                zIndex: 1,
                paths: path
            });
            createProjectMapObject({
                addoverlay: true,
                isorphan: false,
                save: true,
                polyObject: {
                    type: google.maps.drawing.OverlayType.POLYGON,
                    overlay: projectPolygon
                },
                reportedObject: {
                    overlay: projectPolygon
                }
            });
            break;
        case 1:
            var parcelPolygon = new google.maps.Polygon({
                strokeColor: "#0000AA",
                strokeWeight: 2,
                strokeOpacity: 1.0,
                fillColor: "#FFE400",
                fillOpacity: 0.25,
                zIndex: 1,
                paths: path
            });
            createParcelMapObject({
                addoverlay: true,
                isorphan: false,
                save: true,
                polyObject: {
                    type: google.maps.drawing.OverlayType.POLYGON,
                    overlay: parcelPolygon
                },
                reportedObject: {
                    overlay: parcelPolygon
                }
            });
            break;
        case 2:
            for( var i in path ) {
                createPlotMapObject({
                    addoverlay: true,
                    isorphan: false,
                    save: true,
                    polyObject: {
                        type: google.maps.drawing.OverlayType.MARKER,
                        overlay: path[i]
                    }
                });
            }
            break;
        }
    }

    setCoordinateState('');
}



function loadEditPolygonModal(object) {
    switch(object.objectType) {
    case mapObjectType.Project:
        $('#projectBoundaryEdit').modal('show');
        break;
    case mapObjectType.Parcel:
        $('#parcelEdit').modal('show');
        break;
    case mapObjectType.Plot:
        $('#plotEdit').modal('show');
        break;
    }
}

function hideEditPolygonModal() {
    switch(clickedObject.objectType) {
    case mapObjectType.Project:
        $('#projectBoundaryEdit').modal('hide');
        break;
    case mapObjectType.Parcel:
        $('#parcelEdit').modal('hide');
        break;
    case mapObjectType.Plot:
        $('#plotEdit').modal('hide');
        break;
    }
}

function setCoordinateState(type) {
    switch(type) {
    case 'project':
        enterCoordinateState = mapObjectType.Project;
        break;
    case 'parcel':
        enterCoordinateState = mapObjectType.Parcel;
        break;
    case 'plot':
        enterCoordinateState = mapObjectType.Plot;
        break;
    default:
        enterCoordinateState = null;
    }
}
