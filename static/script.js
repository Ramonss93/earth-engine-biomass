biomass = {}

biomass.boot = function(eeMapId, eeToken, callback) {
    google.load("visualization", "1.0");
    google.load("jquery", "1");
    google.load("maps", "3");

    google.setOnLoadCallback(function(){
        var mapType = biomass.App.getEeMapType(eeMapId, eeToken);
        var app = new biomass.App(mapType);
        if (typeof callback === "function") {
            callback();
        }
    });
}


biomass.App = function(mapType) {
    this.map = this.createMap(mapType);
    this.initPanButton(this, $(".pan-button"), this.map);
    this.initPixelButton(this, $(".pixel-button"), this.map);
    this.initRegionButton(this, $(".region-button"), this.map);
    this.initMapClicked(this, this.map);
}

biomass.App.EE_URL = "https://earthengine.googleapis.com";
biomass.App.DEFAULT_ZOOM = 12;
biomass.App.DEFAULT_CENTER = {lng: -93.95336151123047, lat: 47.9533748859759};
biomass.App.STATUS = {NORMAL:0, PICK_UP_PIXEL:1, PICK_UP_REGION:2};
biomass.App.prototype._current_status = biomass.App.STATUS.NORMAL;

biomass.App.getEeMapType = function(eeMapId, eeToken) {
    var eeMapOptions = {
        getTileUrl:function(tile, zoom) {
            var url = biomass.App.EE_URL + "/map/";
            url += [eeMapId, zoom, tile.x, tile.y].join("/");
            url += "?token=" + eeToken;
            return url;
        },
        tileSize: new google.maps.Size(256, 256)
    };
    return new google.maps.ImageMapType(eeMapOptions);
}

biomass.App.prototype.createMap = function(mapType) {
    var mapOptions = {
        backgroundColor: '#333333',
        center: biomass.App.DEFAULT_CENTER,
        disableDefaultUI: true,
        zoom: biomass.App.DEFAULT_ZOOM,
        fullscreenControl: false,
        mapTypeControl: true,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.RIGHT_TOP,
        }
    }
    var mapEl = $('.bm-map').get(0);
    var map = new google.maps.Map(mapEl, mapOptions);
    map.overlayMapTypes.push(mapType);
    return map;
}

biomass.App.prototype.initMapClicked = function(self, map) {
    map.addListener('click', function(e) {
        if (self._current_status == biomass.App.STATUS.PICK_UP_PIXEL) {
            console.log(e.latLng.lat() + ", " + e.latLng.lng());
            self.waiting(); 
            self.getPixelValue(self, e.latLng.lat(), e.latLng.lng());
        }
    });
}

biomass.App.prototype.initPixelButton = function(self, btn, map) {
    $(btn).click(function(e){
        self._current_status = biomass.App.STATUS.PICK_UP_PIXEL;
        map.setOptions({draggableCursor:'crosshair'});
    });
}

biomass.App.prototype.initRegionButton = function(self, btn, map) {
    $(btn).click(function(e){
        self._current_status = biomass.App.STATUS.PICK_UP_REGION;
        map.setOptions({draggableCursor:'cell'});
    });
}

biomass.App.prototype.initPanButton = function(self, btn, map) {
    $(btn).click(function(e){
        self._current_status = biomass.App.STATUS.NORMAL;
        map.setOptions({draggableCursor:''});
    });
}

biomass.App.prototype.getPixelValue = function(self, lat, lng) {
    $.ajax({
        type: 'GET',
        async: true,
        url: '/pixelVal?',
        dataType: 'json',
        data: {'lat':lat, 'lng':lng},
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Accept', 'application/json');
        },
        success: function(data) {
            self.showPixelVal(lat, lng, data);
        },
        error: function(data) {
            alert(data);
        }
    });
}

biomass.App.prototype.showPixelVal = function(lat, lng, val) {
    var content = "<center><table class='bm-table'>";
    content += "<tr><td>BIOMASS</td><td>" + (val['b1'] == null ? 'No Data' : val['b1'])+ "</td></tr>";
    content += "<tr><td>LATITUDE</td><td>" + lat + "</td></tr>";
    content += "<tr><td>LONGITUDE</td><td>" + lng + "</td></tr>";
    content += "</table></center>";
    $('.bm-console').html(content);    
}

biomass.App.prototype.waiting = function() {
    $(".bm-console").html("<center><div data-loader='circle'></div></center>")
}

biomass.App.prototype.fmtCoor = function(coor) {
    return Math.round(coor * 1000) / 1000.0 
}

