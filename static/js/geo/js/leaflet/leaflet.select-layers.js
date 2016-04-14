// Copyright (c) 2013, Sanin ALeksey aka vogdb

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

/**
 * Created: vogdb Date: 4/30/13 Time: 6:07 PM
 */

L.Control.SelectLayers = L.Control.ActiveLayers.extend({

  _initLayout: function () {
    var className = 'leaflet-control-layers'
    var container = this._container = L.DomUtil.create('div', className)

    L.DomEvent.disableClickPropagation(container)
    if (!L.Browser.touch) {
      L.DomEvent.on(container, 'mousewheel', L.DomEvent.stopPropagation)
    } else {
      L.DomEvent.on(container, 'click', L.DomEvent.stopPropagation)
    }

    var form = this._form = L.DomUtil.create('form', className + '-list')

    if (this.options.collapsed) {
      var link = this._layersLink = L.DomUtil.create('a', className + '-toggle', container)
      link.href = '#'
      link.title = 'Layers'

      if (L.Browser.touch) {
        L.DomEvent
          .on(link, 'click', L.DomEvent.stopPropagation)
          .on(link, 'click', L.DomEvent.preventDefault)
          .on(link, 'click', this._expand, this)
      } else {
        L.DomEvent
          .on(container, 'mouseover', this._expand, this)
          .on(container, 'mouseout', this._collapse, this)
        L.DomEvent.on(link, 'focus', this._expand, this)
      }

      this._map.on('movestart', this._collapse, this)
    } else {
      this._expand()
    }

    this._baseLayersList = L.DomUtil.create('select', className + '-base', form)
    L.DomEvent.on(this._baseLayersList, 'change', this._onBaseLayerOptionChange, this)
    this._separator = L.DomUtil.create('div', className + '-separator', form)
    this._overlaysList = L.DomUtil.create('div', className + '-overlays', form)

    container.appendChild(form)
  },

  _onBaseLayerOptionChange: function () {
    var selectedLayerIndex = this._baseLayersList.selectedIndex
    var selectedLayerOption = this._baseLayersList.options[selectedLayerIndex]
    var selectedLayer = this._layers[selectedLayerOption.layerId]

    this._changeBaseLayer(selectedLayer.layer)
  },

  _changeBaseLayer: function (layer) {
    //to be compatible with parent
    this._handlingClick = true

    this._map.addLayer(layer)
    this._map.removeLayer(this._activeBaseLayer)
    this._map.setZoom(this._map.getZoom())
    this._map.fire('baselayerchange', {layer: layer})
    this._activeBaseLayer = layer

    //to be compatible with parent
    this._handlingClick = false
  },

  _addItem: function (obj) {
    if (obj.overlay) {
      //overlay items is handled the same as before
      return L.Control.Layers.prototype._addItem.call(this, obj)
    } else {
      var option = this._createOptionElement(obj)
      this._baseLayersList.appendChild(option)
    }
  },

  _createOptionElement: function (obj) {
    var option = document.createElement('option')
    option.layerId = L.stamp(obj.layer)
    option.innerHTML = obj.name
    if (this._map.hasLayer(obj.layer)) {
      option.setAttribute('selected', true)
    }
    return option
  }

})

L.control.selectLayers = function (baseLayers, overlays, options) {
  return new L.Control.SelectLayers(baseLayers, overlays, options)
}