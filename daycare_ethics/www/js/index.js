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
            app.current_casus = data.id;
            localStorage.setItem('case_data_' + data.id, JSON.stringify(data));
            $('#plate .week-number').html(data.week);
            $('#case-text').html(data.text);
            $('#case-proposition').html(data.proposition);
            var image_size = (app.viewport.width - 20) * app.viewport.pixelRatio;
            var img = $('<img>')
                .attr('src', '/media/' + data.picture + '/' + image_size)
                .load(function() {
                    $('#case-display').append(img);
                });
            $('#plate').css('background-color', data.background);
            if (localStorage.getItem('has_voted_' + data.id)) {
                app.displayVotes();
            }
        });
    },
    
    submitVote: function(choice) {
        var id = app.current_casus,
            case_data = JSON.parse(localStorage.getItem('case_data_' + id));
        if (choice === 'yes' || choice === 'no') {
            $.get('/case/vote', {
                'id': id,
                'choice': choice
            }).done(function(data) {
                if (data === 'success') {
                    case_data[choice] += 1;
                    localStorage.setItem('has_voted_' + id, true);
                    localStorage.setItem('case_data_' + id, JSON.stringify(case_data));
                    app.displayVotes();
                }
            });
        }
    },
    
    displayVotes: function() {
        var id = app.current_casus,
            case_data = JSON.parse(localStorage.getItem('case_data_' + id)),
            yes_count = case_data.yes,
            no_count = case_data.no;
        $('#plate > a').hide();
        $('#yes_count').html('ja ' + yes_count);
        $('#no_count').html(no_count + ' nee');
        $('#no_bar').width(
            $('#plate').innerWidth() - $('#yes_count').width() - $('#no_count').width() - 36
        );
        $('#yes_bar').css('width', 100 * yes_count / (yes_count + no_count) + '%');
    },
    
    // Bind Event Listeners
    // Bind any events that are required on startup. Common events are:
    // 'load', 'deviceready', 'offline', and 'online'.
    bindEvents: function() {
        var vote_buttons = $('#plate > a');
        $(vote_buttons[0]).on('mousedown touchdown', function() {
            app.submitVote('yes');
        });
        $(vote_buttons[1]).on('mousedown touchdown', function() {
            app.submitVote('no');
        });
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
