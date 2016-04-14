
var drawStateType = {
    NORMAL: 0,
    PLANTPLOT: 1,
    PLANTPARCEL: 2,
    PLANTPROJECT: 3,
    DRAWPLOT: 4,
    DRAWPARCEL: 5,
    DRAWPROJECT: 6
};



var projectContainer = new MapObjectContainer('projectboundary'); //This needs to be project boundary, as these are project boundaries, not projects.
var parcelContainer = new MapObjectContainer('parcel');
var plotContainer = new MapObjectContainer('plot');
var drawState = drawStateType.NORMAL;
var enterCoordinateState = null


/**
 * Handles the mapTypeChanged event. Sets the label color to the appropriate
 * color given the new map type text color
 * @param  {map object} googleMap The map object
 * @return {none}           [description]
 */
function mapTypeChanged(googleMap) {
    if (googleMap == null )
        return;

    var fg = googleMap.getCurrentMapType().getTextColor();
    projectContainer.setLabelColor(fg);
    parcelContainer.setLabelColor(fg);
    plotContainer.setLabelColor(fg);
}

function mapMouseMoved(latlng) {
    switch(drawState) {
    case drawStateType.PLANTPLOT:
        current = plotContainer.getCurrent();
        break;
    case drawStateType.PLANTPARCEL:
        current = parcelContainer.getCurrent();
        break;
    case drawStateType.PLANTPROJECT:
        current = projectContainer.getCurrent();
        break;
    default:
        current = null;
        break;
    }

    if ( current != null ){
        current.setCenter(latlng);
    }
}

/**
 * Close the polygon
 * @param  {Overlay} polygon The overlay we need to close
 * @return {null}         Return null if there is an error.
 */
function closePolygon(polygon) {
    if (polygon == null)
        return;

    var n = polygon.getPath().length;
    if ( n < 3 )
        return;

    var latLngStart = polygon.getPath().getAt(0);
    var latLngEnd = polygon.getPath().getAt(n-1);
    if ( !latLngStart.equals(latLngEnd)) {
        polygon.getPath().push(new google.maps.LatLng(latLngStart.lat(), latLngStart.lng()));
    }
}

function createProjectMapObject( options ) {
    var projectObject = new MapObject();
    var projectOptions = {
        id: options['id'],
        name: "project_boundary_" + projectIncrement,
        objectType: mapObjectType.Project,
        polygon: {
            type: options['polyObject'].type,
            overlay: options['polyObject'].overlay
        },
        icon: overlayMarkers.PROJECT,
        polyOptions: overlayOptions.PROJECT,
        reportPolyOptions: overlayOptions.REPORTPROJECT,
        resourceUri: options['resourceUri'],
        reportedPolygon: options['reportedObject'],
        area: options['area'],
        area_reported: options['area_reported']

    };

    if ( options['name'] != undefined ) {;
        projectOptions['name'] = options['name'];
    }
    projectObject.construct(projectOptions);
    projectIncrement++;
    if( options['save'] )
        projectObject.setUpdate(updateType.ADD);

    if ( options['isorphan'] ) {
        projectObject.orphan();
    }

    projectContainer.add(projectObject);
    if ( options['addoverlay'] ) {
        projectObject.addToMap(googleMap);
    }

    projectObject.updateMarker();
    return projectObject;
}

function createParcelMapObject( options ) {
    var parcelObject = new MapObject();
    var parcelOptions = {
        id: options['id'],
        name: "parcel_" + parcelIncrement,
        objectType: mapObjectType.Parcel,
        polygon: {
            type: options['polyObject'].type,
            overlay: options['polyObject'].overlay
        },
        icon: overlayMarkers.PARCEL,
        polyOptions: overlayOptions.PARCEL,
        reportPolyOptions: overlayOptions.REPORTPARCEL,
        resourceUri: options['resourceUri'],
        reportedPolygon: options['reportedObject'],
        area: options['area'],
        area_reported: options['area_reported']
    }

    if ( options['name'] ) {
        parcelOptions['name'] = options['name'];
    }
    parcelObject.construct(parcelOptions);
    parcelIncrement++;

    if ( options['save'] )
        parcelObject.setUpdate(updateType.ADD);

    if ( options['isorphan'] ) {
        parcelObject.orphan();
    }

    parcelContainer.add(parcelObject);
    if ( options['addoverlay'] ) {
        parcelObject.addToMap(googleMap);
    }


    parcelObject.updateMarker();
    return parcelObject;
}

function createPlotMapObject( options ) {
    var plotObject = new MapObject();
    var plotOptions = {
        id: options['id'],
        name: "plot_" + plotIncrement,
        objectType: mapObjectType.Plot,
        polygon: {
            type: options['polyObject'].type,
            overlay: options['polyObject'].overlay
        },
        icon: overlayMarkers.PLOT,
        polyOptions: overlayOptions.PLOT,
        reportPolyOptions: overlayOptions.REPORTPLOT,
        resourceUri: options['resourceUri'],
        reportedPolygon: options['reportedObject'],
        shape: options['shape'],
        shapeReported: options['shapeReported'],
        dimensions: options['dimensions'],
        dimensionsReported: options['dimensionsReported'],
        parcel: options['parcel'],
        area: options['area'],
        area_reported: options['area_reported']
    };

    if (plotOptions.shape == undefined) {
        plotOptions['shape'] = 'unknown';
    }

    if ( options['name'] ) {
        plotOptions['name'] = options['name'];
    }
    plotObject.construct(plotOptions);
    plotIncrement++;
    if( options['save'] )
        plotObject.setUpdate(updateType.ADD);
    if ( options['isorphan'] )
        plotObject.orphan();

    plotContainer.add(plotObject);

    if ( options['addoverlay'] ) {
        plotObject.addToMap(googleMap);
    }

    plotObject.updateMarker();
    return plotObject;
}

function showAll(container) {
    for ( var i = 0; i < container.length; i++ ) {
        container[i].show();
    }
}

function clearMap() {
    projectContainer.deleteAll();
    parcelContainer.deleteAll();
    plotContainer.deleteAll();
}

function showAll() {
    projectContainer.showAll();
    parcelContainer.showAll();
    plotContainer.showAll();
}

function deleteMapObject() {
    clickedObject.setUpdate(updateType.REMOVE);
    clickedObject.save();

    hideEditPolygonModal();
    clickedObject = null;
}

function editPolygon(type) {
    if( $('#map' + type).is(":checked") ) {
        setSelection(clickedObject.polyObject);
    }
    else {
        setSelection(clickedObject.reportedPolyObject);
    }

    hideEditPolygonModal();
}

function change_proj_type(type) {
    if ( type == 'map' ) {
        clickedObject.editMode_reported = false;

        if( clickedObject.polyObject.getPath().getLength() <= 0 ) {
            $('#projEditButton').addClass('disabled');
        } else {
            $('#projEditButton').removeClass('disabled');
        }

        $('#projbndarea').html("" + clickedObject.area.toFixed(2) + " ha");
    } else if ( type == 'reported' ) {
        clickedObject.editMode_reported = true;

        if( clickedObject.reportedPolyObject.getPaths().getLength() <= 0) {
            $('#projEditButton').addClass('disabled');
        } else {
            $('#projEditButton').removeClass('disabled');
        }
        $('#projbndarea').html("" + clickedObject.reportedArea.toFixed(2) + " ha");
    }
}

function change_parcel_type(type) {
    if ( type == 'map' ) {
        clickedObject.editMode_reported = false;

        if( clickedObject.polyObject.getPath().getLength() <= 0 ) {
            $('#parcelEditButton').addClass('disabled');
        } else {
            $('#parcelEditButton').removeClass('disabled');
        }

        $('#parcelarea').html("" + clickedObject.area.toFixed(2) + " ha");
    } else if ( type == 'reported' ) {
        clickedObject.editMode_reported = true;

        if( clickedObject.reportedPolyObject.getPaths().getLength() <= 0) {
            $('#parcelEditButton').addClass('disabled');
        } else {
            $('#parcelEditButton').removeClass('disabled');
        }
        $('#parcelarea').html("" + clickedObject.reportedArea.toFixed(2) + " ha");
    }
}

function enableDrawing(type) {
    ReDrawing = true;
    var polyOptions = null;
    generalSetCurrent(clickedObject);
    if( clickedObject.editMode_reported) {
        clickedObject.reportedPolyObject.setMap(null);
        if( type == 'project') {
            drawState = drawStateType.DRAWPROJECT;
            polyOptions = overlayOptions.REPORTPROJECT;
        } else if( type == 'parcel') {
            drawState = drawStateType.DRAWPARCEL;
            polyOptions = overlayOptions.REPORTPARCEL;
        } else {
            drawState = drawStateType.DRAWPLOT;
            polyOptions = overlayOptions.REPORTPLOT;
        }
    } else {
        clickedObject.polyObject.setMap(null);
        if ( type == 'project') {
            drawState = drawStateType.DRAWPROJECT;
            polyOptions = overlayOptions.PROJECT;
        } else if( type == 'parcel') {
            drawState = drawStateType.DRAWPARCEL;
            polyOptions = overlayOptions.PARCEL;
        } else {
            drawState = drawStateType.DRAWPLOT;
            polyOptions = overlayOptions.PLOT;
        }
    }

    drawingManager.setOptions({
        drawingMode: google.maps.drawing.OverlayType.POLYGON,
        polygonOptions: polyOptions
    });

    if( type == 'project' )
        $('#projectBoundaryEdit').modal('hide');
    else if ( type == 'parcel' )
        $('#parcelEdit').modal('hide');
}

function doneClicked() {
    clickedObject = null;
}