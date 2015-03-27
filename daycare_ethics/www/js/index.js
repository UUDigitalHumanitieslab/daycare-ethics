/*
    (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
    Author: Julian Gonggrijp
*/
var app = {
    // Application Constructor
    initialize: function() {
        $('#reflection-response').validate({submitHandler: this.submitReply});
        $('#reflection-captcha').validate({submitHandler: this.submitCaptcha});
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
        $.get('/reflection/').done(function(data) {
            if (data.token) localStorage.setItem('token', data.token);
            app.current_reflection = data.id;
            localStorage.setItem('reflection_data_' + data.id, JSON.stringify(data));
            localStorage.setItem('last_retrieve', data.since);
            $('#mirror .week-number').html(data.week);
            $('#reflection-text').html(data.text);
            _(data.responses).each(app.appendReply);
            nickname = localStorage.getItem('nickname');
            if (nickname) $('#form-field-p').val(nickname);
            if (data.closure) {
                if (new Date(data.closure) <= new Date()) {
                    $('#reflection-response').hide();
                    $('#reflection-closure-announce').hide();
                } else {
                    $('#reflection-closure-date').text(data.closure);
                    $('#reflection-closed-notice').hide();
                }
            } else {
                $('#reflection-closed-notice').hide();
                $('#reflection-closure-announce').hide();
            }
        });
        $.get('/tips/').done(function(data) {
            // Load labour code tips
            $.each(data.labour, function( index, labour ) {
                var tip = $('<li>').html(labour.title);
                $("#labour-code-tips").append(tip);
            });
            // Load website links
            $.each(data.site, function( index, site ) {
                var tip = $('<li>').html('<a href="' + site.href + '">' + site.title + '</a>');
                $("#website-links").append(tip);
            });
            // Load book tips
            $.each(data.book, function( index, book ) {
                var tip = $('<li>')
                    .append($('<h3>').html(book.title).css('white-space', 'normal'))
                    .append($('<p>').html(book.author));
                $("#book-tips").append(tip);
            });
            // We need to refresh the listviews on load.
            $('.tips-list').listview('refresh');
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
                localStorage.setItem('token', data.token);
                if (data.status === 'success') {
                    case_data[choice] += 1;
                    localStorage.setItem('has_voted_' + id, true);
                    localStorage.setItem('case_data_' + id, JSON.stringify(case_data));
                    app.displayVotes();
                }
            });
        }
    },
    
    submitReply: function(form) {
        $(form).hide();
        var id = app.current_reflection,
            reflection_data = JSON.parse(localStorage.getItem('reflection_data_' + id)),
            nickname = $('#form-field-p').val(),
            message = $('#form-field-r').val();
        localStorage.setItem('nickname', nickname);
        $.post('/reflection/' + id + '/reply', {
            p: nickname,
            r: message,
            t: localStorage.getItem('token'),
            'last-retrieve': localStorage.getItem('last_retrieve'),
            ca: $('#form-field-ca').val()
        }).done(function(data) {
            localStorage.setItem('token', data.token);
            switch (data.status) {
            case 'success':
                app.appendReply({
                    pseudonym: nickname,
                    'message': message
                });
                $(form).find('#form-field-r').val('');
                $(form).show();
                break;
            case 'ninja':
                $('#ninja-message').popup('open', {positionTo: 'window'});
                $('#reply-submitted').remove();
                _(data.new).each(app.appendReply);
                $(form).show();
                localStorage.setItem('last_retrieve', data.since);
                break;
            case 'captcha':
                $('#captcha-challenge').text(data.captcha_challenge);
                $('#captcha-popup').popup('open', {positionTo: 'window'});
            }
        }).fail(function(jqXHR) {
            if ( jqXHR.status == 400 &&
                 jqXHR.responseText && jqXHR.responseText[0] == '{' ) {
                data = JSON.parse(jqXHR.responseText);
                localStorage.setItem('token', data.token);
                switch (data.status) {
                case 'closed':
                    $('#reflection-closed-popup').popup('open', {positionTo: 'window'});
                    $('#reflection-closure-announce').hide();
                    $('#reflection-closed-notice').show();
                    break;
                case 'invalid':
                    $('#reflection-invalid-popup').popup('open', {positionTo: 'window'});
                    $('#reflection-response').show();
                }
            }
        })
        $('#form-field-ca').val('');
    },
    
    submitCaptcha: function(form) {
        $('#captcha-popup').popup('close');
        app.submitReply($('#reflection-response'));
    },
    
    appendReply: function(data) {
        var upvotes = data.up || 0,
            downvotes = data.down || 0,
            score = app.getScore(upvotes, downvotes);
        var div = $('<div></div>');
        div.attr('id', 'reply-' + (data.id || 'submitted'));
        var date = '<span class="reply-date">' + (data.submission || 'net') + '</span>';
        var pseudonym = '<span class="reply-nick">' + data.pseudonym + '</span>';
        var synopsis = $('<h3 class="reply-synopsis"></h3>').append(date + ' ' + pseudonym);
        div.append(synopsis);
        div.append(date);
        div.append(pseudonym);
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

        // If score is lower than treshold, show the synopsis and display as collapsible.
        if (score < 0.35) {
            synopsis.show();
            $('#reply-' + data.id + ' .reply-synopsis .reply-nick').html('spam');
            div.collapsible({ mini: true, collapsedIcon: 'arrow-r', expandedIcon: 'arrow-d' });
        }
        // Otherwise, hide the synopsis.
        else {
            synopsis.hide();
        }
    },

    submitReplyVote: function(id, choice) {
        if (choice === 'up' || choice === 'down') {
            $.post('/reply/' + id + '/moderate/', {
                'choice': choice,
                't': localStorage.getItem('token')
            }).done(function(data) {
                localStorage.setItem('token', data.token);
                if (data.status === 'success') {
                    // hide reply vote buttons on success, and add success message
                    $('#reply-' + id + ' .reply-vote').hide();
                    $('#reply-' + id + ' .reply-vote:last')
                        .after($('<em>')
                        .text('Bedankt voor je stem!')
                        .css('color', 'green'));
                }
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
