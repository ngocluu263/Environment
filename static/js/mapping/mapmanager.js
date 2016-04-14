function MapManager() {
	var mapObjects;
	var currId;
	var currView;

	function initialize() {
		mapObjects = new Array();
		currId = {
			'project' : 0,
			'parcel' : 0,
			'plot' : 0
		};

		currView = {
			'project' : {
				'markers' : true,
				'mapped' : true,
				'reported' : true,
				'labels' : true
			},
			'parcel' : {
				'markers' : true,
				'mapped' : true,
				'reported' : true,
				'labels' : true
			},
			'plot' : {
				'markers' : true,
				'mapped' : true,
				'reported' : true,
				'labels' : true
			}		
		}
	}

	this.Add = function(mapObject) {
		mapObjects.push(mapObject);

		var mapped = currView[mapObject.pType]['mapped'];
		var reported = currView[mapObject.pType]['reported'];
		var markers = currView[mapObject.pType]['markers'];
		var labels = currView[mapObject.pType]['labels'];

		if(mapObject.polyObj) {
			if(mapped) {
				mapObject.polyObj.show();
			}	
			else {
				mapObject.polyObj.hide();
			}				
		}

		if(mapObject.markObj) {
			if(markers) {
				mapObject.markObj.show();
			}
			else {
				mapObject.markObj.hide();
			}
		}

		if(mapObject.labelObj) {
			if(labels) {
				mapObject.labelObj.show();
			}
			else {
				mapObject.labelObj.hide();
			}	
		}	
	}

	this.Clear = function() {
		initialize();
		map.graphics.clear();
	}

	this.GetAll = function() {
		return mapObjects;
	}

	this.GetId = function(pType) {
		return currId[pType]++;
	}

	this.GetView = function(pType, view) {
		return currView[pType][view];
	}
	
	this.SetView = function(pType, mapped, markers, reported, labels) {
		for(var i=0; i < mapObjects.length; i++) {
			var mObj = mapObjects[i];
			if(mObj.pType == pType) {
				if(mObj.polyObj) {
					if(mapped) {
						mObj.polyObj.show();
					}	
					else {
						mObj.polyObj.hide();
					}				
				}

				if(mObj.markObj) {
					if(markers) {
						mObj.markObj.show();
					}
					else {
						mObj.markObj.hide();
					}
				}

				if(mObj.labelObj) {
					if(labels) {
						mObj.labelObj.show();
					}
					else {
						mObj.labelObj.hide();
					}
				}

			}
		}	
		currView[pType]['markers'] = markers;
		currView[pType]['mapped'] = mapped;
		currView[pType]['reported'] = reported;
		currView[pType]['labels'] = labels;
	}

	initialize();
}