var updateType = {
    NONE: 0,
    ADD: 1,
    REMOVE: 2,
    CHANGE: 3
};

var mapObjectType = {
    Project : 0,
    Parcel : 1,
    Plot : 2
}

var mapShapeType = {
    UNKNOWN: "unknown",
    SQUARE : "square",
    RECTANGLE : "rectangle",
    CIRCLE : "circle",
    POLYGON : "polygon"
}

var overlayOptions = {
    PROJECT: {
        strokeColor: "#00FF00",
        strokeWeight: 2,
        strokeOpacity: 1.0,
        fillColor: '#00FF00',
        fillOpacity: 0.25
    },
    PARCEL: {
        strokeColor: '#0000FF',
        strokeWeight: 2,
        strokeOpacity: 1.0,
        fillColor: '#0000FF',
        fillOpacity: 0.25
    },
    PLOT: {
        strokeColor: "#FF0000",
        strokeWeight: 2,
        strokeOpacity: 1.0,
        fillColor: "#FF0000",
        fillOpacity: 0.25
    },
    REPORTPROJECT: {
        strokeColor: "#00AA00",
        strokeWeight: 2,
        strokeOpacity: 1.0,
        fillColor: "#FFE400",
        fillOpacity: 0.25,
        zIndex: 1
    },
    REPORTPARCEL: {
        strokeColor: "#0000AA",
        strokeWeight: 2,
        strokeOpacity: 1.0,
        fillColor: "#FFE400",
        fillOpacity: 0.25,
        zIndex: 1
    },
    REPORTPLOT: {
        strokeColor: "#AA0000",
        strokeWeight: 2,
        strokeOpacity: 1.0,
        fillColor: "#FFE400",
        fillOpacity: 0.25,
        zIndex: 1
    }
}

var clickedObject = null;

label_defaultstyle = "font-size: 13px; font-family: Arial,Helvetica,sans-serif; font-weight: bold;color:white;text-shadow:2px 2px #000";

var overlayMarkers = {
    PROJECT: {
        url: '/static/images/grnball.png',
        anchor: new google.maps.Point(7,7)
    },
    PARCEL: {
        url: '/static/images/bluball.png',
        anchor: new google.maps.Point(7,7)
    },
    PLOT: {
        url: '/static/images/redball.png',
        anchor: new google.maps.Point(7,7)
    }
};

var mapObjectIncrement = 0;
var projectIncrement = 1;
var parcelIncrement = 1;
var plotIncrement = 1;

// These methods do not require a csrf token
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function postObject(uri, object, dataToSave) {
    return $.ajax({
        url: uri,
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(dataToSave),
        beforeSend: function(xhr, settings){
            $("#loaderDiv").show();
            var csrftoken = getCookie('csrftoken');
            if ( !csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        },
        complete: function(){
            setTimeout(function() {$("#loaderDiv").hide();
            }, 1000);
        },
        success: function(data) {
            setTimeout(function() {$("#saved").show();
            }, 1000);
            setTimeout(function() {$("#saved").hide();
            }, 2000);
            object['id'] = data['id'];
            object['resource_uri'] = data['resource_uri'];
            if( data['area_mapped'] != null)
                object['area'] = data['area_mapped'];
            else
                object['area'] = 0.0;

            if( data['area_reported'] != null)
                object['reportedArea'] = data['area_reported']
            else
                object['reportedArea'] = 0.00;

            if ( data['parcel'] != undefined )
                object['parcel'] = data['parcel'];
        },
        error: function(xhr){
            if(xhr.status === 201) {
                var responseJson = JSON.parse(responseText);
                object['id'] = responseJson['id'];
                object['resource_uri'] = responseJson['resource_uri'];
                return;
            }
            setTimeout(function() {$("saveError").show()}, 1000);
            setTimeout(function() {$("saveError").hide()}, 2000);
        }
    })
}

function patchObject(uri, object, dataToSave) {
    return $.ajax({
        url: uri,
        type: 'PATCH',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(dataToSave),
        tryCount: 0,
        retryLimit: 3,
        beforeSend: function(xhr, settings){
            $("#loaderDiv").show();
            var csrftoken = getCookie('csrftoken');
            if ( !csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        },
        complete: function(){
            setTimeout(function() {$("#loaderDiv").hide();
            }, 1000);
        },
        success: function(data) {
            setTimeout(function() {$("#saved").show();
            }, 1000);
            setTimeout(function() {$("#saved").hide();
            }, 2000);
            if( data['area_mapped'] != null)
                object['area'] = data['area_mapped'];
            else
                object['area'] = 0.0;

            if( data['area_reported'] != null)
                object['reportedArea'] = data['area_reported']
            else
                object['reportedArea'] = 0.00;
        },
        error: function(data) {
            this.tryCount++;
            if( this.tryCount <= this.retryLimit) {
                $.ajax(this);
                return;
            }
            setTimeout(function() {$("saveError").show()}, 1000);
            setTimeout(function() {$("saveError").hide()}, 2000);
        }
    })
}

function deleteObject(uri, object) {
    return $.ajax({
        url: uri,
        type: 'DELETE',
        tryCount: 0,
        retryLimit: 3,
        beforeSend: function(xhr, settings){
            $("#loaderDiv").show();
            var csrftoken = getCookie('csrftoken');
            if ( !csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        },
        complete: function(){
            setTimeout(function() {$("#loaderDiv").hide();
            }, 1000);
        },
        success: function(data) {
            setTimeout(function() {$("#saved").show();
            }, 1000);
            setTimeout(function() {$("#saved").hide();
            }, 2000);
            object.container.remove(object);
        },
        error: function(data) {
            this.tryCount++;
            if(this.tryCount <= this.retryLimit) {
                $.ajax(this);
                return;
            }
            setTimeout(function() {$("saveError").show()}, 1000);
            setTimeout(function() {$("saveError").hide()}, 2000);
        }
    });
}

function MapObject() {
    this.id = -1;
    this.resource_uri = null;
    this.labid = null;
    this.polyObject = null;
    this.markerObject = null;
    this.reportedPolyObject = null;
    this.labelObject = null;
    this.center = new google.maps.LatLng(0,0);
    this.objectName = null;
    this.project = 'test';
    this.canEdit = false;
    this.hidden = false;
    this.viewMarker = false;
    this.viewPolygon = false;
    this.viewReportedPolygon = false;
    this.viewLabel = false;
    this.orphaned = false;
    this.on_map = false;
    this.editMode_reported = false;
    this.vert = '';
    this.reportedVert = '';
    this.update = updateType.NONE;
    this.objectType = null;
    this.path = null;
    this.shape = null;
    this.shapeReported = null;
    this.container = null;
    this.update_list = [];
    this.saveInterval = null;
    this.area = 0.00;
    this.reportedArea = 0.00;

    this.dimensions = null;
    this.dimensionsReported = null;
    this.parcel = '';



    // Data is a dictionary with the following values:
    //      name : string
    //      objectType : mapObjectType
    //      polygon: Polygon object
    //      icon: overlayMarkers
    //      polyOptions : overlayOptions
    //      reportPolyOptions : overlayOptions
    //      shape : mapShapeType
    this.construct = function(data) {
        this.id = data['id'];

        this.objectName = data.name;
        this.resource_uri = data['resourceUri'];
        this.labid = data.name + this.id;
        this.objectType = data.objectType;
        this.path = new google.maps.MVCArray;
        this.shape = data.shape;
        this.shapeReported = data.shapeReported;
        this.dimensions = data.dimensions;
        this.dimensionsReported = data.dimensionsReported;

        if ( data['parcel'] != undefined ) {
            this.parcel = data['parcel'];
        }
        console.log(data.polygon);
        console.log(data.reportedPolygon);

        if ( data.polygon == null || data.polygon == undefined ) {
            this.markerObject = new google.maps.Marker({
                position: new google.maps.LatLng(0,0),
                icon: data.icon
            });
            this.center = this.markerObject.getPosition();
            this.polyObject = new google.maps.Polygon(data.polyOptions);
        }
        else if ( data.polygon.type == google.maps.drawing.OverlayType.MARKER) {
            this.markerObject = data.polygon.overlay;
            this.center = this.markerObject.getPosition();
            this.polyObject = new google.maps.Polygon(data.polyOptions);
            this.polyObject.getPath().push(this.center);
        } else {
            this.polyObject = data.polygon.overlay;
            this.markerObject = new google.maps.Marker({
                position: getPolyBounds(data.polygon.overlay).getCenter(),
                icon: data.icon,
            });
        }

        this.reportedPolyObject = new google.maps.Polygon(data.reportPolyOptions);
        if (data.reportedPolygon && data.reportedPolygon.overlay != undefined && data.reportedPolygon.overlay != null) {
            this.reportedPolyObject = data.reportedPolygon.overlay;
        }
        this.labelObject = new ELabel(this.markerObject.getPosition(), new google.maps.Size(8,0), '<font id="' + this.labid + '" style="' + label_defaultstyle + '">' + data.name + '</font>', 'elabelstyle1', 0, false );
        if ( data['area'] != null ) {
            this.area = data['area'];
        }

        if ( data['area_reported'] != null )
            this.reportedArea = data['area_reported'];
        
        if (this.polyObject)
            this.polyObject.meta = this;
        if (this.markerObject)
            this.markerObject.meta = this;
        if (this.reportedPolyObject)
            this.reportedPolyObject.meta = this;
        if (this.labelObject)
            this.labelObject.meta = this;

        this.setEventListeners();
    }

    this.save = function() {
        obj = this;
        // NEED TO SERIALIZE VERTICES TO POST TO THE DATABASE
        var mappedVerticesArray = this.polyObject.getPaths();
        var mappedVertices = '';
        mappedVerticesArray.forEach(function(elem, index){
            elem.forEach(function(e,i){
                mappedVertices += e.lng() + ',' + e.lat();
                if( i != elem.getLength() - 1 )
                    mappedVertices += ',';
            });
        });

        var reportedVerticesArray = this.reportedPolyObject.getPath();
        var reportedVertices = '';

        if (reportedVerticesArray != null )
            for ( var i = 0; i < reportedVerticesArray.getLength(); i++) {
                reportedVertices += reportedVerticesArray.getAt(i).lng() + ',' + reportedVerticesArray.getAt(i).lat();
                if( i != reportedVerticesArray.getLength() - 1 ) {
                    reportedVertices += ',';
                }
            }

        // reportedVerticesArray.forEach(function(elem, index){
        //     elem.forEach(function(e,i){
        //         reportedVertices += e.lat() + ',' + e.lng();
        //         if(i != elem.getLength() - 1 )
        //             reportedVertices += ',';
        //     });
        // });

        if (reportedVertices == '') {
            reportedVertices = null;
        }

        if(this.update == updateType.ADD) {
            if(this.resource_uri != null && this.id != -1) {
                alert('Object already exists');
                return;
            }


            if(this.objectType == mapObjectType.Project) {
                postObject('/api/v1/projectboundary/', this, {
                    name: obj.objectName,
                    vertices_mapped: mappedVertices,
                    vertices_reported: reportedVertices,
                    project: '/api/v1/project/' + project_id + '/'
                });
            }
            else if(this.objectType == mapObjectType.Parcel) {
                postObject('/api/v1/parcel/', this, {
                    name: obj.objectName,
                    vertices_mapped: mappedVertices,
                    vertices_reported: reportedVertices,
                    project: '/api/v1/project/' + project_id + '/'
                });
            }
            else if(this.objectType == mapObjectType.Plot) {
                postObject('/api/v1/plot/', this, {
                    name: obj.objectName,
                    vertices_mapped: mappedVertices,
                    vertices_reported: reportedVertices,
                    project: '/api/v1/project/' + project_id + '/',
                    shape_mapped: obj.shape,
                })
            }
        }
        else if ( this.update == updateType.CHANGE) {
            if( this.resource_uri != null ) {
                if(this.objectType == mapObjectType.Project) {
                    patchObject(obj.resource_uri, this, {
                        name: obj.objectName,
                        vertices_mapped: mappedVertices,
                        vertices_reported: reportedVertices,
                        project: '/api/v1/project/' + project_id + '/'
                    });
                }
                else if(this.objectType == mapObjectType.Parcel) {
                    patchObject(obj.resource_uri, this, {
                        name: obj.objectName,
                        vertices_mapped: mappedVertices,
                        vertices_reported: reportedVertices,
                        project: '/api/v1/project/' + project_id + '/'
                    });
                }
                else if(this.objectType == mapObjectType.Plot) {
                    patchObject(obj.resource_uri, this, {
                        name: obj.objectName,
                        vertices_mapped: mappedVertices,
                        vertices_reported: reportedVertices,
                        project: '/api/v1/project/' + project_id + '/',
                        shape_mapped: obj.shape,
                        shape_reported: obj.shapeReported,
                        dimensions_mapped: obj.dimensions,
                        dimensions_reported: obj.dimensionsReported,
                        parcel: obj.parcel,
                        area_mapped: obj.area,
                        area_reported: obj.reportedArea
                    })
                }
            }
        }
        else if ( this.update == updateType.REMOVE ) {
            if( this.resource_uri != null ) {
                if(this.objectType == mapObjectType.Project) {
                    deleteObject(obj.resource_uri, obj);
                }
                else if(this.objectType == mapObjectType.Parcel) {
                    deleteObject(obj.resource_uri, obj);
                }
                else if(this.objectType == mapObjectType.Plot) {
                    deleteObject(obj.resource_uri, obj);
                }
            }
        }
        this.setUpdate(updateType.NONE);
    }

    this.copyAttributes = function( mapObject ) {
        this.dbid = mapObject.dbid;
        this.objectName = mapObject.name;
        this.project = mapOpbject.project;
        this.canEdit = mapObject.canEdit;
        this.hidden = mapObject.hidden;
        this.viewMarker = mapObject.viewMarker;
        this.viewPolygon = mapObject.viewPolygon;
        this.viewReportedPolygon = mapObject.viewReportedPolygon;
        this.viewLabel = mapObject.viewLabel;
        this.orphaned = mapObject.orphaned;
        this.editMode_reported = mapObject.editMode_reported;
        this.vert = mapObject.vert;
        this.reportedVert = mapObject.reportedVert;
        this.update = mapObject.update;
    };

    this.copy = function( mapObject ) {
        this.copyAttributes( mapObject );
        this.id = mapObject.id;
        this.labid = mapObject.labid;
        this.polyObject = mapObject.polyObject;
        this.markerObject = mapObject.markerObject;
        this.reportedPolyObject = mapObject.reportedPolyObject;
        this.labelObject = mapObject.labelObject;
    };

    this.isOrphaned = function() {
        return this.orphaned;
    }

    this.adopt = function() {
        this.orphaned = false;
    }

    this.orphan = function() {
        this.orphaned = true;
    }

    this.setUpdate = function(update) {
        obj = this;
        if( update != updateType.NONE && update != undefined)
            this.update_list.push(update);
        else
            this.update = update;

        if ( this.saveInterval == null ) {
            this.saveInterval = setInterval(function(){
                if(obj.update == updateType.NONE || obj.update == undefined){
                    obj.update = obj.update_list.shift();
                    obj.save();
                }

                if (obj.update_list.length == 0) {
                    clearInterval(obj.saveInterval);
                    obj.saveInterval = null;
                }
            }, 50);
        }
        return this.saveInterval;
    }

    this.getUpdate = function() {
        return this.update();
    }

    this.setDbid = function(dbid) {
        if (dbid == null)
            return false;
        this.dbid = dbid;
        return true;
    }

    this.setResourceId = function(resourceUri) {
        this.resourceUri = resourceUri;
    }

    this.isHidden = function() {
        return this.hidden;
    }

    this.hide = function() {
        if (this.polyObject == null)
            return;

        if (this.reportedPolyObject)
            this.reportedPolyObject.setVisible(false);

        this.polyObject.setVisible(false);
        this.markerObject.setVisible(false);
        this.labelObject.hide();
        this.hidden = true;
    }

    this.show = function() {
        if (this.polyObject == null)
            return;

        if (this.reportedPolyObject)
            this.reportedPolyObject.setVisible(true);
        this.polyObject.setVisible(true);
        this.markerObject.setVisible(true);
        this.labelObject.show();

        this.hidden = false;
    }

    this.setViewLabel = function(vw) {
        if ( this.labelObject == null )
            return;

        if ( vw )
            this.labelObject.show();
        else
            this.labelObject.hide();
        this.viewLabel = vw;
        return true;
    }

    this.setViewMarker = function(vw) {
        if ( this.markerObject == null )
            return;

        if ( vw )
            this.markerObject.setVisible(true);
        else
            this.markerObject.setVisible(false);

        this.viewMarker = vw;
        return true;
    }

    this.setViewPolygon = function(vw) {
        if ( this.polyObject == null )
            return;

        if ( vw )
            this.polyObject.setVisible(true);
        else
            this.polyObject.setVisible(false);

        this.viewPolygon = vw;
    }

    this.setViewReportedPolygon = function(vw) {
        if ( this.reportedPolyObject == null )
            return;

        if ( vw )
            this.reportedPolyObject.setVisible(true);
        else
            this.reportedPolyObject.setVisible(false);

        this.viewReportedPolygon = vw;
    }

    this.setLabelColor = function(color) {
        if ( this.labid == null )
            return;
        var eid = document.getElementById(this.labid);
        if ( eid != undefined )
            eid.style.color = clr;
    }

    this.setLabelText = function(text) {
        if ( this.labelObject != null )
            this.labelObject.setContents('<font id="' + this.labid + '" style="' + label_defaultstyle + '">' + text + '</font>');
    }

    this.updateLabel = function() {
        this.setLabelText(this.objectName);
    }

    this.getCenter = function() {
        return this.center;
    }

    this.setCenter = function(latlng) {
        if ( latlng == null )
            return;
        this.center = new google.maps.LatLng(latlng.lat(), latlng.lng());

        if(this.on_map) {
            this.markerObject.setPosition(this.center);
            this.labelObject.setPoint(this.center);
        }
    }

    this.addToMap = function(map) {
        if ( this.polyObject )
            this.polyObject.setMap(map);

        if ( this.reportedPolyObject )
            this.reportedPolyObject.setMap(map);

        if ( this.markerObject )
            this.markerObject.setMap(map);

        if ( this.labelObject ) {
            this.labelObject.setMap(map);
            this.labelObject.setPoint(this.center);

            this.setLabelText(this.objectName);
            this.setLabelColor("white");
        }
        this.on_map = true;
    }

    this.removeFromMap = function(gmap) {
        if ( this.polyObject )
            this.polyObject.setMap(null);
        if ( this.reportedPolyObject )
            this.reportedPolyObject.setMap(null);
        if ( this.markerObject )
            this.markerObject.setMap(null);
        if ( this.labelObject )
            this.labelObject.setMap(null);
    }

    this.updateMarker = function() {
        this.setCenter(getPolyBounds(this.polyObject).getCenter());
    }

    this.setEventListeners = function() {
        if (this.polyObject)
            google.maps.event.clearInstanceListeners(this.polyObject);
        if (this.reportedPolyObject)
            google.maps.event.clearInstanceListeners(this.reportedPolyObject);
        if (this.polyObject)
            google.maps.event.clearInstanceListeners(this.polyObject.getPath());

        var obj = this;
        if (this.polyObject) {
        google.maps.event.addListener(this.polyObject.getPath(), "set_at", function(event) {
            obj.updateMarker();
            obj.setUpdate(updateType.CHANGE);
        });

        google.maps.event.addListener(this.polyObject.getPath(), "insert_at", function(event) {
            obj.updateMarker();
            obj.setUpdate(updateType.CHANGE);
        });
        }

        if( this.reportedPolyObject && this.reportedPolyObject.getPath() != undefined ) {
            google.maps.event.addListener(this.reportedPolyObject.getPath(), "insert_at", function(event){
                obj.setUpdate(updateType.CHANGE);
            });

            google.maps.event.addListener(this.reportedPolyObject.getPath(), "set_at", function(event){
                obj.setUpdate(updateType.CHANGE);
            });
        }
        
        if (this.polyObject)
        google.maps.event.addListener(this.polyObject, "click", function(event) {
            generalSetCurrent(obj, obj.objectType)
            drawState = drawStateType.NORMAL;

            if(obj.polyObject.getEditable() || obj.reportedPolyObject.getEditable()) {
                obj.polyObject.setEditable(false);
                obj.reportedPolyObject.setEditable(false);

                if(drawingManager.getDrawingMode() != null) {
                    drawingManager.setDrawingMode(null);
                    google.maps.event.trigger(drawingManager, 'overlaycomplete', {type: 'none'});
                }
            }
            else {
                generalSetCurrent(obj, obj.objectType);
                clickedObject = obj;
                loadEditPolygonModal(obj);
            }
        });

        google.maps.event.addListener(this.markerObject, "click", function(event){
            generalSetCurrent(obj, obj.objectType);
            clickedObject = obj;
            loadEditPolygonModal(obj);
        });
        
        if (this.polyObject)
        google.maps.event.addListener(this.polyObject, "rightclick", function(event){
            generalSetCurrent(obj, obj.objectType);
            turnOffDrawingMode();
            clickedObject = null;
        });



    }

}

/*
This function was copied and pasted from http://www.w3schools.com/js/js_cookies.asp
*/
function setCookie(cname, cvalue) {
    // setting the cookie to expire at 0 causes the cookie to expire when the browser/tab closes.
    // make it so the cookie expires when the session closes / or a different project is selected.

    // var d = new Date();
    // d.setTime(d.getTime() + (365*24*60*60*1000));
    var name = cname + "="+cvalue+"; ";
    // var expires = "expires="+d.toUTCString()+"; ";
    var expires = "expires=0; path=/; "
    document.cookie = name + expires;
}

/*
This function was copied and pasted from http://www.w3schools.com/js/js_cookies.asp
*/
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');

    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) != -1) return c.substring(name.length,c.length);
    }
    return "";
}

function checkCookie(cookieName, input) {
    var cookie = getCookie(cookieName);
   // console.log(cookieName+": "+cookie);

    if(cookie != ""){ //cookie exists
        if(cookie != input){ //cookie must be updated
            setCookie(cookieName, input);
            cookie = getCookie(cookieName);
            //console.log(cookieName+": "+cookie);
            return true;
        }
        else{return false;} // cookie == input, so the checkmark has not changed, do nothing
    }
    else{   //cookie does not exist
        //console.log("cookie named "+cookieName+" does not exist. creating cookie...")
        setCookie(cookieName, input);
        cookie = getCookie(cookieName);
        //console.log(cookieName+": "+cookie);
        return true;
    }
}


function checkCookieExists(cookieName) {
    var cookie = getCookie(cookieName);
    // check if cookie exists
    return cookie != ""
}

function MapObjectContainer(objecttype) {
    this.objects = [];
    this.current = null;

    var type = objecttype;
    if (objecttype == "projectboundary") {
        var type = 'project';
    }

    this.viewMarker = getCookie('showMarkers'+type);
    this.viewPolygon = getCookie('showPolygons'+type);
    //console.log('showPolygons'+objecttype+": "+this.viewPolygon);
    this.viewReportedPolygon = getCookie('showReportedPolygons'+type);
    //console.log('showReportedPolygons'+objecttype+": "+this.viewReportedPolygon);
    this.viewLabel = getCookie('showLabels'+type);
    //console.log('showLabels'+objecttype+": "+this.viewLabel);
    this.containertype = objecttype;


    this.length = function() {
        return this.objects.length;
    }

    this.getArray = function() {
        return this.objects;
    }

    this.setCurrent = function(obj) {
        this.current = obj;
    }

    this.add = function(obj) {
        this.objects.push(obj);
        obj.container = this;
        this.current = obj;
        obj.setViewMarker(this.viewMarker);
        obj.setViewPolygon(this.viewPolygon);
        obj.setViewReportedPolygon(this.viewReportedPolygon);
        obj.setViewLabel(this.viewLabel);
    }

    this.remove = function(obj) {
        var index = this.objects.indexOf(obj);
        if ( index > -1 ) {
            this.objects.splice(index, 1);
        }

        obj.removeFromMap();
        obj.container = null;
    }
    this.getCurrent = function() {
        return this.current;
    }

    this.showAll = function() {
        for ( var i in this.objects ) {
            this.objects[i].show();

        }
    }

    this.hideAll = function() {
        for ( var i in this.objects ) {
            i.hide();
        }
    }

    this.clear = function() {
        for ( var i in this.objects ) {
            this.objects[i].removeFromMap();
        }
    }

    this.deleteAll = function() {
        for ( var i in this.objects ) {
            deleteObject(this.objects[i].resource_uri, this.objects[i]);
        }
    }

    this.load = function() {
        temp = this;
        return $.ajax({
            url: '/api/v1/' + temp.containertype + '/?project=' + project_id,
            type: 'GET',
            dataType: 'json',
            success: finishLoad
        });
    }

    this.setViewMarkerAll = function(vw) {
        //console.log('in setViewMarkerAll');
        this.viewMarker = vw;


        //console.log("this.objects"+this.objects)

        for ( var i in this.objects ) {
            //console.log('in setViewMarkerAll loop');
            var success = this.objects[i].setViewMarker(vw);
        }
    }

    this.setViewPolygonAll = function(vw) {

        this.viewPolygon = vw;

        for ( var i in this.objects ) {
            this.objects[i].setViewPolygon(vw);
        }
    }

    this.setViewReportedPolygonAll = function(vw) {

        this.viewReportedPolygon = vw;

        for ( var i in this.objects ) {
            this.objects[i].setViewReportedPolygon(vw);
        }
    }

    this.setViewLabelAll = function(vw) {

        this.viewLabel = vw;

        for ( var i in this.objects ) {
            var success = this.objects[i].setViewLabel(vw);
            //console.log(this.objects[i].name+".setViewLabel(vw): "+success);
        }
    }
}
//  END OF MAP OBJECT CONTAINER


function initSetView(){
    var types = ["project", "parcel", "plot"]
    var containers = {
        project: projectContainer,
        parcel: parcelContainer,
        plot: plotContainer
    }

    for(var type in types){         //for each type, get cookies and set views

        var markersCookie = getCookie('showMarkers'+types[type]);
        var polygonsCookie = getCookie('showPolygons'+types[type]);
        var reportedCookie = getCookie('showReportedPolygons'+types[type]);
        var labelsCookie = getCookie('showLabels'+types[type]);

        document.getElementById("show_markers_"+types[type]).checked = (markersCookie === "true");
        document.getElementById("show_mapped_poly_"+types[type]).checked = (polygonsCookie === "true");
        document.getElementById("show_reported_poly_"+types[type]).checked = (reportedCookie === "true");
        document.getElementById("show_labels_"+types[type]).checked = (labelsCookie === "true") ;

        if(markersCookie === ""){

            setCookie('showMarkers'+types[type],true);
            containers[types[type]].setViewMarkerAll(true);

        }

        else containers[types[type]].setViewMarkerAll((markersCookie === "true"));

        if(polygonsCookie === ""){

          setCookie('showPolygons'+types[type],true);
          containers[types[type]].setViewPolygonAll(true);

        }

        else containers[types[type]].setViewPolygonAll((polygonsCookie === "true"));

        if(reportedCookie === ""){

           setCookie('showReportedPolygons'+types[type],true);
            containers[types[type]].setViewReportedPolygonAll(true);

        }

        else containers[types[type]].setViewReportedPolygonAll((reportedCookie === "true"));

        if(labelsCookie === ""){

            setCookie('showLabels'+types[type],true);
            containers[types[type]].setViewLabelAll(true);

        }

        else containers[types[type]].setViewLabelAll((labelsCookie === "true"));
    }

    return true;
}

function setView(type){
    var containers = {
        project: projectContainer,
        parcel: parcelContainer,
        plot: plotContainer
    }

    var showMarkers = document.getElementById("show_markers_"+type).checked
    var showPolygons = document.getElementById("show_mapped_poly_"+type).checked
    var showReportedPolygons = document.getElementById("show_reported_poly_"+type).checked
    var showLabels = document.getElementById("show_labels_"+type).checked

    var changed = checkCookie('showMarkers'+type, showMarkers, containers[type]);
    if (changed){
        containers[type].setViewMarkerAll(showMarkers);
    }

    changed = checkCookie('showPolygons'+type, showPolygons, containers[type]);
    if (changed){
        containers[type].setViewPolygonAll(showPolygons);
    }

    changed = checkCookie('showReportedPolygons'+type, showReportedPolygons, containers[type]);
    if (changed){
        containers[type].setViewReportedPolygonAll(showReportedPolygons);
    }

    changed = checkCookie('showLabels'+type, showLabels, containers[type]);
    if (changed){
        containers[type].setViewLabelAll(showLabels);
    }

}



function getPolyBounds(polyobj){
    console.log(polyobj);
    console.log(polyobj.getPath());
    console.log(polyobj.getPaths());
    var bounds = new google.maps.LatLngBounds();
    if (polyobj)
        for(var i=0; i < polyobj.getPath().getLength(); i++) {
            bounds.extend(polyobj.getPath().getAt(i));
        }
    return bounds;
 }

 function generalSetCurrent(obj, type) {
    switch(type) {
    case mapObjectType.Project:
        projectContainer.setCurrent(obj);
        break;
    case mapObjectType.Parcel:
        parcelContainer.setCurrent(obj);
        break;
    case mapObjectType.Plot:
        plotContainer.setCurrent(obj);
        break;
    }
 }

 function turnOffDrawingMode() {
    if(drawingManager.getDrawingMode() != null) {
        deleteOverlay = true;
        drawingManager.setDrawingMode(null);
        drawState = drawStateType.NORMAL;
        google.maps.event.trigger(drawingManager, 'overlaycomplete', {type: 'none'});
    }
 }

 function finishLoad(data) {
    $.each(data["objects"], function(v, boundary){
        var mappedVertices = boundary["vertices_mapped"];
        var reportedVertices = boundary["vertices_reported"]
        var mappedPath = new google.maps.MVCArray();
        var reportedPath = new google.maps.MVCArray();
        if ( mappedVertices != null ) {
            mappedVertices = mappedVertices.split(',');
            for( var i = 1; i < mappedVertices.length; i += 2) {
                mappedPath.push(new google.maps.LatLng(parseFloat(mappedVertices[i]), parseFloat(mappedVertices[i-1])));
            }
        }
        if ( reportedVertices != null ) {
            reportedVertices = reportedVertices.split(',');

            for( var i = 1; i < reportedVertices.length; i+= 2) {
                reportedPath.push(new google.maps.LatLng(parseFloat(reportedVertices[i]), parseFloat(reportedVertices[i-1])));
            }
        }
        var container = null;
        if ( boundary["resource_uri"].search('projectboundary') != -1){
            var projectPolygon = null;
            var reportedPolygon = null;
            if (mappedPath.getLength() > 0) {
                projectPolygon = new google.maps.Polygon({
                    fillColor: '#00FF00',
                    strokeColor: '#00FF00',
                    zIndex: 0,
                    paths: mappedPath
                });
            }
            if (reportedPath.getLength() > 0) {
                reportedPolygon = new google.maps.Polygon({
                    strokeColor: "#00AA00",
                    strokeWeight: 2,
                    strokeOpacity: 1.0,
                    fillColor: "#FFE400",
                    fillOpacity: 0.25,
                    paths: reportedPath
                });
            }
            if (reportedPolygon || projectPolygon) {
            createProjectMapObject({
                addoverlay: true,
                isorphan: false,
                polyObject: {
                    type: google.maps.drawing.OverlayType.POLYGON,
                    overlay: projectPolygon
                },
                reportedObject: {
                    overlay: reportedPolygon
                },
                save: false,
                id: boundary['id'],
                resourceUri: boundary['resource_uri'],
                name: boundary['name'],
                area : boundary['area_mapped'],
                area_reported: boundary['area_reported']
            });
            }
            container = projectContainer;
        }
        else if( boundary["resource_uri"].search('parcel') != -1) {
            var parcelPolygon = null;
            var reportedPolygon = null;
            if (mappedPath.getLength() > 0) {
            parcelPolygon = new google.maps.Polygon({
                fillColor: '#0000FF',
                strokeColor: '#0000FF',
                zIndex: 0,
                paths: mappedPath
            });
            }
            if (reportedPath.getLength() > 0) {
            reportedPolygon = new google.maps.Polygon({
                strokeColor: "#0000AA",
                strokeWeight: 2,
                strokeOpacity: 1.0,
                fillColor: "#FFE400",
                fillOpacity: 0.25,
                paths: reportedPath
            });
            }
            if (reportedPolygon || parcelPolygon)
            createParcelMapObject({
                addoverlay: true,
                isorphan: false,
                polyObject: {
                    type: google.maps.drawing.OverlayType.POLYGON,
                    overlay: parcelPolygon
                },
                reportedObject: {
                    overlay: reportedPolygon
                },
                save: false,
                id: boundary['id'],
                resourceUri: boundary['resource_uri'],
                name: boundary['name'],
                area : boundary['area_mapped'],
                area_reported: boundary['area_reported']
            });
            container = parcelContainer;
        }
        else {
            var plotPolygon = null;
            var reportedPolygon = null;
            if (mappedPath.getLength() > 0) {
            plotPolygon = new google.maps.Polygon({
                fillColor: '#FF0000',
                strokeColor: '#FF0000',
                zIndex: 3,
                paths: mappedPath
            });
            }
            var reportedPolygonOptions = {
                strokeColor: "#AA0000",
                strokeWeight: 2,
                strokeOpacity: 1.0,
                fillColor: "#FFE400",
                fillOpacity: 0.25,
            }

            if ( reportedPath.getLength() != 0 ) {
                reportedPolygonOptions['paths'] = reportedPath;
                reportedPolygon = new google.maps.Polygon(reportedPolygonOptions);
            }
            if (plotPolygon || reportedPolygon)
            createPlotMapObject({
                addoverlay: true,
                isorphan: false,
                polyObject: {
                    type: google.maps.drawing.OverlayType.POLYGON,
                    overlay: plotPolygon
                },
                reportedObject: {
                    overlay: reportedPolygon
                },
                save: false,
                id: boundary['id'],
                resourceUri: boundary['resource_uri'],
                name: boundary['name'],
                shape: boundary['shape_mapped'],
                shapeReported: boundary['shape_reported'],
                dimensions: boundary['dimensions_mapped'],
                dimensionsReported: boundary['dimensions_reported'],
                parcel: boundary['parcel'],
                area : boundary['area_mapped'],
                area_reported: boundary['area_reported']
            });
            container = plotContainer;
        }
    });
    if ( data.meta.next != null ) {
        return $.ajax({
            url: data.meta.next,
            type: 'GET',
            dataType: 'json',
            success: finishLoad
        });
    }

 }
function testSuccess(data){

}
