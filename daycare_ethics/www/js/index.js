/*
    (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
    Author: Julian Gonggrijp
*/
var app = {
    // Application Constructor
    initialize: function() {
        $('#reflection-response').validate({submitHandler: this.submitReply});
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
            localStorage.setItem('token', data.token);
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
        $.get('/reflection/').done(function(data) {
            app.current_reflection = data.id;
            localStorage.setItem('reflection_data_' + data.id, JSON.stringify(data));
            localStorage.setItem('token', data.token);
            $('#mirror .week-number').html(data.week);
            $('#reflection-text').html(data.text);
            _(data.responses).each(app.appendReply);
        });
    },
    
    submitVote: function(choice) {
        var id = app.current_casus,
            case_data = JSON.parse(localStorage.getItem('case_data_' + id));
        if (localStorage.getItem('has_voted_' + id)) return;
        if (choice === 'yes' || choice === 'no') {
            $.post('/case/vote', {
                'id': id,
                'choice': choice,
                't': localStorage.getItem('token')
            }).done(function(data) {
                if (data.status === 'success') {
                    case_data[choice] += 1;
                    localStorage.setItem('has_voted_' + id, true);
                    localStorage.setItem('case_data_' + id, JSON.stringify(case_data));
                    app.displayVotes();
                }
                localStorage.setItem('token', data.token);
            });
        }
    },
    
    submitReply: function(form) {
        var id = app.current_reflection,
            reflection_data = JSON.parse(localStorage.getItem('reflection_data_' + id)),
            nickname = $('#form-field-p').val(),
            message = $('#form-field-r').val();
        localStorage.setItem('nickname', nickname);
        $(form).hide();
        $.post('/reflection/' + id + '/reply', {
            p: nickname,
            r: message,
            t: localStorage.getItem('token')
        }).done(function(data) {
            localStorage.setItem('token', data.token);
            switch (data.status) {
            case 'success':
                app.appendReply({
                    pseudonym: nickname,
                    'message': message
                });
                $(form).show();
            default:
                console.log(data);
            }
        }).fail(function(jQxhr) {
            console.log(jQxhr);
        })
    },
    
    appendReply: function(data) {
        var upvotes = data.up || 0,
            downvotes = data.down || 0,
            score = app.getScore(upvotes, downvotes);
        var div = $('<div></div>');
        div.attr('id', 'reply-' + (data.id || 'submitted'));
        if (score < 0.35) div.addClass('troll');
        div.append($('<span class="reply-date"></span>').text(data.submission || 'net'));
        div.append('<span class="reply-nick">' + data.pseudonym + '</span>');
        div.append($('<span class="reply-content"></span>').html(data.message));
        if (data.id) {
            div.append('<br>');
            div.append($('<a href="#">leer ik van</a>')
                        .addClass('reply-vote ui-btn ui-icon-plus ui-btn-icon-left')
                        .data('for', data.id)
                        .on('touchstart mousedown', function() {
                            app.submitReplyVote(data.id, 'up');
                        }));
            div.append($('<a href="#">kwade wil</a>')
                        .addClass('reply-vote ui-btn ui-icon-minus ui-btn-icon-right')
                        .data('for', data.id)
                        .on('touchstart mousedown', function() {
                            app.submitReplyVote(data.id, 'down');
                        }));
        }
        div.appendTo('#reflection-discussion');
    },

    submitReplyVote: function(id, choice) {
        if (choice === 'up' || choice === 'down') {
            $.post('/reply/' + id + '/moderate/', {
                'choice': choice,
                't': localStorage.getItem('token')
            }).done(function(data) {
                if (data.status === 'success') {
                    // hide reply vote buttons on success
                    $('#reply-' + id + ' .reply-vote').hide();
                    $('#reply-' + id).append($('<h3>').text('Bedankt voor je stem!'));
                }
                localStorage.setItem('token', data.token);
            });
        }
    },
    
    // Wilson score for Bernoulli distribution
    // (upper bound of 95% conf.int. of proportion of upvotes)
    getScore: function(upvotes, downvotes) {
        var total = upvotes + downvotes;
        if (total === 0) return 1;
        var z = 1.96,
            zz = z * z,
            upObserved = 1.0 * upvotes / total,
            errorTerm = zz / (2 * total),
            sumOfSquares = upObserved * (1 - upObserved) + zz / (4 * total),
            rootTerm = z * Math.sqrt(sumOfSquares / total),
            enumerator = upObserved + errorTerm + rootTerm,
            denominator = 1 + zz / total;
        return enumerator / denominator;
    },
    
    displayVotes: function() {
        var id = app.current_casus,
            case_data = JSON.parse(localStorage.getItem('case_data_' + id)),
            yes_count = case_data.yes,
            no_count = case_data.no;
        $('#plate > a').hide();
        $('#yes_count').html('ja ' + yes_count);
        $('#no_count').html(no_count + ' nee');
        $('#no_bar').width($(window).width() - 15 * 8);
        $('#yes_bar').css('width', 100 * yes_count / (yes_count + no_count) + '%');
    },
    
    // Bind Event Listeners
    // Bind any events that are required on startup. Common events are:
    // 'load', 'deviceready', 'offline', and 'online'.
    bindEvents: function() {
        var vote_buttons = $('#plate > a');
        $(vote_buttons[0]).on('mousedown touchstart', function() {
            app.submitVote('yes');
        });
        $(vote_buttons[1]).on('mousedown touchstart', function() {
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
