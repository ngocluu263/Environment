
function loadInitialValues() {
    document.getElementById('coord1lat').value = '';
    document.getElementById('coord1lng').value = '';

    if( clickedObject.editMode_reported ) {

        document.getElementById('coord1lat').value = clickedObject.center.lat();
        document.getElementById('coord1lng').value = clickedObject.center.lng();


        if ( clickedObject.dimensionsReported != null ) {
            if ( clickedObject.dimensionsReported.search('x') != -1) {
                var dim = clickedObject.dimensionsReported.split('x');
                document.getElementById('plotxdim').value = dim[0];
                document.getElementById('plotydim').value = dim[1];

                document.getElementById('plotarea').innerHTML = parseFloat(dim[0]) * parseFloat(dim[1]);
                clickedObject.reportedArea = parseFloat(dim[0]) * parseFloat(dim[1]);
            } else {
                document.getElementById('plotxdim').value = clickedObject.dimensionsReported;
                document.getElementById('plotarea').innerHTML = parseFloat(clickedObject.dimensionsReported) * parseFloat(clickedObject.dimensionsReported) * 3.14;
                clickedObject.reportedArea = parseFloat(clickedObject.dimensionsReported) * parseFloat(clickedObject.dimensionsReported) * 3.14;
            }
        }
    } else {

        document.getElementById('coord1lat').value = clickedObject.center.lat();
        document.getElementById('coord1lng').value = clickedObject.center.lng();
        if ( clickedObject.dimensions != null ) {
            if ( clickedObject.dimensions.search('x') != -1) {
                var dim = clickedObject.dimensions.split('x');
                document.getElementById('plotxdim').value = dim[0];
                document.getElementById('plotydim').value = dim[1];
                document.getElementById('plotarea').innerHTML = parseFloat(dim[0]) * parseFloat(dim[1]);
                clickedObject.area = parseFloat(dim[0]) * parseFloat(dim[1]);
            } else {
                document.getElementById('plotxdim').value = clickedObject.dimensions;
                document.getElementById('plotarea').innerHTML = parseFloat(clickedObject.dimensions) * parseFloat(clickedObject.dimensions) * 3.14;
                clickedObject.area = parseFloat(clickedObject.dimensions) * parseFloat(clickedObject.dimensions) * 3.14;
            }
        }
    }
}

$('#plotEdit').on('show.bs.modal', function(event){
    $('#plotname').val(clickedObject.objectName);
   var url = '/api/v1/plot/' + clickedObject.id  + '/';
   $.get(url, function(data1, status){
           var polyTest = data1.poly_reported;                  
           if(data1.poly_reported != null){
             clickedObject.editMode_reported = true;
           }
	    if( clickedObject.editMode_reported ) {
		$('#repplot').prop('checked', true);

		if( clickedObject.reportedPolyObject.getPath().getLength() <= 0) {
		    $('#plotEditButton').addClass('disabled');
		} else {
		    $('#plotEditButton').removeClass('disabled');
		}
	    } else {
		$('#mapplot').prop('checked', true);

		if( clickedObject.polyObject.getPath().getLength() <= 0) {
		    $('#plotEditButton').addClass('disabled');
		} else {
		    $('#plotEditButton').removeClass('disabled');
		}
	    }     

    switch(clickedObject.shape) {
    case mapShapeType.RECTANGLE:
        document.getElementById('rectangle').checked=true;
        enable_shape_type('rectangle');
        break;
    case mapShapeType.CIRCLE:
        document.getElementById('circle').checked=true;
        enable_shape_type('circle');
        break;
    default:
        document.getElementById('unknown').checked=true;
        enable_shape_type('unknown');
        break;
    }
    $.ajax({
        url: '/api/v1/parcel-with-hidden-no-plots/?project=' + project_id,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            document.getElementById('parcelnames').innerHTML = '';
            $.each(data['objects'], function(index, parcel) {
                var data = $('<option/>');
                data.attr({'value': parcel['resource_uri']}).text(parcel['name']);
                if( parcel['resource_uri'] == clickedObject.parcel) {
                    data.attr({'selected': 'selected'});
                }

                $('#parcelnames').append(data);
            });
        }
    }); 
    loadInitialValues();
   });
});

function rectangle_shape_disable() {
    document.getElementById('coord1lat').disabled = true;
    document.getElementById('coord1lng').disabled = true;
}

function rectangle_shape_enable() {
    document.getElementById('coord1lat').disabled = false;
    document.getElementById('coord1lng').disabled = false;
}

function change_plot_type(type) {
    if( type == 'map') {
        clickedObject.editMode_reported = false;
        switch(clickedObject.shape) {
        case mapShapeType.RECTANGLE:
            document.getElementById('rectangle').checked=true;
            enable_shape_type('rectangle');
            break;
        case mapShapeType.CIRCLE:
            document.getElementById('circle').checked=true;
            enable_shape_type('circle');
            break;
        default:
            document.getElementById('unknown').checked=true;
            enable_shape_type('unknown');
            break;
        }
        loadInitialValues();
    } else {
        clickedObject.editMode_reported = true;
        switch(clickedObject.shapeReported) {
        case mapShapeType.RECTANGLE:
            document.getElementById('rectangle').checked=true;
            enable_shape_type('rectangle');
            break;
        case mapShapeType.CIRCLE:
            document.getElementById('circle').checked=true;
            enable_shape_type('circle');
            break;
        default:
            document.getElementById('unknown').checked=true;
            enable_shape_type('unknown');
            break;
        }

        loadInitialValues();
    }
}

function enable_shape_type(value) {
    if ( value == 'rectangle' ) {                           // Modify plotEdit for rectangles
        $('#plotydim').prop('disabled', false);
        $('#plotydimbutton').prop('disabled', false);
        $('#plotxdim').prop('disabled', false);
        $('#plotxdimbutton').prop('disabled', false);

        rectangle_shape_disable();

        document.getElementById('llpoints').innerHTML = "<b>Center Point:";
        //document.getElementById('utmpoints').innerHTML = '<b>Center Point (UTM):';
        document.getElementById('plotdimlabel').innerHTML = "<b>Plot Dimensions:</b>";
        document.getElementById('plotdimlabel').style.color = "rgb(53,57,71)";

    } else if ( value == 'circle' ) {                       // Modify plotEdit for circles
        $('#plotydim').prop('disabled', true);
        $('#plotydimbutton').prop('disabled', true);
        $('#plotxdim').prop('disabled', false);
        $('#plotxdimbutton').prop('disabled', false);
        document.getElementById('plotdimlabel').style.color = "rgb(53,57,71)";
        document.getElementById('plotdimlabel').innerHTML = "<b>Plot Radius:</b>";
        document.getElementById('llpoints').innerHTML = "<b>Center Point:";
        //document.getElementById('utmpoints').innerHTML = '<b>Center Point (UTM):';
        rectangle_shape_disable();

    } else {                                                // Modify plotEdit for unknown
        $('#plotxdim').prop('disabled', true);
        $('#plotxdimbutton').prop('disabled', true);
        $('#plotydim').prop('disabled', true);
        $('#plotydimbutton').prop('disabled', true);

        rectangle_shape_disable();

        document.getElementById('llpoints').innerHTML = "<b>Center Point:";
        document.getElementById('plotdimlabel').innerHTML = "<b>Plot Dimensions:</b>";
        //document.getElementById('utmpoints').innerHTML = '<b>Center Point (UTM):';
        document.getElementById('plotdimlabel').style.color = "grey";
    }
}

$('#plotEdit').on('submit', function(event) {
    event.preventDefault();
    var temp = clickedObject;

    clickedObject.objectName = document.getElementById('plotname').value;
    clickedObject.updateLabel();

    clickedObject.parcel = $('#parcelnames').val();
    if(clickedObject.editMode_reported) {
        var shape = $('input[name=plotshape]:checked').val();
        switch(shape) {
        case 'circle':
            if ( document.getElementById('plotxdim').value == '' )
                return;

            if( document.getElementById('coord' + 1 + 'lat').value == '' || document.getElementById('coord' + 1 + 'lat') == null )
                    return;
            if ( document.getElementById('coord' + 1 + 'lng').value == '' || document.getElementById('coord' + 1 + 'lng' == null))
                    return;

            var path = new google.maps.MVCArray();
            path.push(new google.maps.LatLng(parseFloat(document.getElementById('coord' + 1 + 'lat').value),parseFloat(document.getElementById('coord' + 1 + 'lng').value) ));
            clickedObject.reportedPolyObject.setPath(path);
            clickedObject.dimensionsReported = document.getElementById('plotxdim').value;
            break;
        case 'rectangle':
            if ( document.getElementById('plotxdim').value == '' || document.getElementById('plotydim').value == '')
                return;

            if( document.getElementById('coord' + 1 + 'lat').value == '' || document.getElementById('coord' + 1 + 'lat') == null )
                    return;
            if ( document.getElementById('coord' + 1 + 'lng').value == '' || document.getElementById('coord' + 1 + 'lng' == null))
                    return;

            var path = new google.maps.MVCArray();
            path.push(new google.maps.LatLng(parseFloat(document.getElementById('coord' + 1 + 'lat').value),parseFloat(document.getElementById('coord' + 1 + 'lng').value) ));

            clickedObject.reportedPolyObject.setPath(path);

            clickedObject.dimensionsReported = document.getElementById('plotxdim').value + 'x' + document.getElementById('plotydim').value;
            break;
        default:
            if( document.getElementById('coord' + 1 + 'lat').value == '' || document.getElementById('coord' + 1 + 'lat') == null )
                    return;
            if ( document.getElementById('coord' + 1 + 'lng').value == '' || document.getElementById('coord' + 1 + 'lng' == null))
                    return;

            var path = new google.maps.MVCArray();
            path.push(new google.maps.LatLng(parseFloat(document.getElementById('coord' + 1 + 'lat').value),parseFloat(document.getElementById('coord' + 1 + 'lng').value) ))
            clickedObject.reportedPolyObject.setPath(path);
            clickedObject.dimensionsReported = null;
            break;
        }
        clickedObject.shapeReported = shape;
    } else {
        var shape = $('input[name=plotshape]:checked').val();
        switch(shape) {
        case 'circle':
            if ( document.getElementById('plotxdim').value == '' )
                return;

            if( document.getElementById('coord' + 1 + 'lat').value == '' || document.getElementById('coord' + 1 + 'lat') == null )
                    return;
            if ( document.getElementById('coord' + 1 + 'lng').value == '' || document.getElementById('coord' + 1 + 'lng' == null))
                    return;

            var path = new google.maps.MVCArray();
            path.push(new google.maps.LatLng(parseFloat(document.getElementById('coord' + 1 + 'lat').value),parseFloat(document.getElementById('coord' + 1 + 'lng').value) ));
            clickedObject.polyObject.setPath(path);
            clickedObject.dimensions = document.getElementById('plotxdim').value;
            break;
        case 'rectangle':
            if ( document.getElementById('plotxdim').value == '' || document.getElementById('plotydim').value == '')
                return;

            if( document.getElementById('coord' + 1 + 'lat').value == '' || document.getElementById('coord' + 1 + 'lat') == null )
                    return;
            if ( document.getElementById('coord' + 1 + 'lng').value == '' || document.getElementById('coord' + 1 + 'lng' == null))
                    return;

            var path = new google.maps.MVCArray();
            path.push(new google.maps.LatLng(parseFloat(document.getElementById('coord' + 1 + 'lat').value),parseFloat(document.getElementById('coord' + 1 + 'lng').value) ));

            clickedObject.polyObject.setPath(path);

            clickedObject.dimensions = document.getElementById('plotxdim').value + 'x' + document.getElementById('plotydim').value;
            break;
        default:
            if( document.getElementById('coord' + 1 + 'lat').value == '' || document.getElementById('coord' + 1 + 'lat') == null )
                    return;
            if ( document.getElementById('coord' + 1 + 'lng').value == '' || document.getElementById('coord' + 1 + 'lng' == null))
                    return;

            var path = new google.maps.MVCArray();
            path.push(new google.maps.LatLng(parseFloat(document.getElementById('coord' + 1 + 'lat').value),parseFloat(document.getElementById('coord' + 1 + 'lng').value) ))
            clickedObject.polyObject.setPath(path);
            clickedObject.dimensions = null;
            break;
        }
        clickedObject.shape = shape;
    }
    clickedObject.setUpdate(updateType.CHANGE);

    loadInitialValues();
})
