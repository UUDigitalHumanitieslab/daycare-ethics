/*
    (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
    Author: Julian Gonggrijp, j.gonggrijp@uu.nl
*/
var app = {
    // Application Constructor
    initialize: function() {
        this.findDimensions();
        this.preloadContent();
        this.bindEvents();
    },
    
    findDimensions: function() {
        this.viewport = {
            width: window.innerWidth,
            height: window.innerHeight,
            pixelRatio: window.devicePixelRatio
        };
    },
    
    preloadContent: function() {
        $.get('/case/').done(function(data) {
            $('#plate .week-number').html(data.week);
            $('#case-text').html(data.text);
            $('#case-proposition').html(data.proposition);
            var image_size = app.viewport.width * app.viewport.pixelRatio;
            var img = $('<img>')
                .attr('src', '/media/' + data.picture + '/' + image_size)
                .load(function() {
                    $('#case-display').append(img);
                });
            $('#plate').css('background-color', data.background);
        });
    },
    
    // Bind Event Listeners
    // Bind any events that are required on startup. Common events are:
    // 'load', 'deviceready', 'offline', and 'online'.
    bindEvents: function() {
        document.addEventListener('deviceready', this.onDeviceReady, false);
    },
    
    // deviceready Event Handler
    // The scope of 'this' is the event. In order to call the 'receivedEvent'
    // function, we must explicitly call 'app.receivedEvent(...);'
    onDeviceReady: function() {
        app.receivedEvent('deviceready');
    },
    
    // Update DOM on a Received Event
    receivedEvent: function(id) {
    }
};
