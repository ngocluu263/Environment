function MapObject(pName, pType, graphic, geometry) {
	this.id = mapManager.GetId(pType);
	this.polyObj = null;
	this.markObj = null;
	this.labelObj = null;
	this.pType = pType;
	this.name = pName;


	// set markobj //
	switch(geometry) {
		case "polygon":
			this.polyObj = graphic;
			console.log(graphic.geometry);
			var coords = graphic.geometry.getCentroid();
			mSymbol = new esri.symbol.PictureMarkerSymbol(markerPictures[pType], 13, 13);
			this.markObj = new esri.Graphic(coords, mSymbol);
			map.graphics.add(this.markObj);
			console.log(coords);
			break;

		case "point":
		case "multipoint":
			this.markObj = graphic;
			break;
	}
	//////////////////

	// set labelObj //
	if(pName == pType)
	{
		this.pName = pType + "_" + this.id;
	}
	text_symbol = new esri.symbol.TextSymbol(this.pName, new esri.symbol.Font(), new esri.Color("white"));
	text_symbol.setOffset(10, 0);
	text_symbol.setHorizontalAlignment("left");

	this.labelObj = new esri.Graphic(this.markObj.geometry, text_symbol);
	map.graphics.add(this.labelObj);
	////////////////


	return this;
	
}