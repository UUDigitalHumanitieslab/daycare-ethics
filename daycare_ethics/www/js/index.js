/*
    (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
    Author: Julian Gonggrijp, j.gonggrijp@uu.nl
*/
var app = {
    // Application Constructor
    initialize: function() {
        this.preloadContent();
        this.bindEvents();
    },
    
    preloadContent: function() {
        $.get('/case/', null, function(data, status) {
            if (status != '200 OK') {
                console.log('No internet connection');
                return;
            }
            $('#plate .week-number').html(data.week);
            $('#case-text').html(data.text);
            $('#case-proposition').html(data.proposition);
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
