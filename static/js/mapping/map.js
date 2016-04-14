$(document).ready(function(){
    var mapType = google.maps.MapTypeId.HYBRID


    function initialize(){
        var mapOptions = {
            mapTypeId : mapType,
            streetViewControl: false
        }

        var map = new google.maps.Map(document.getElementById("mapcanvas"), mapOptions);
    }


    initialize();
})