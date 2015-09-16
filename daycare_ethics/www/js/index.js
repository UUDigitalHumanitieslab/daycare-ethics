/*
    (c) 2014, 2015 Digital Humanities Lab, Utrecht University
    Authors: Julian Gonggrijp, Martijn van der Klis
*/
'use strict';
var app = {
    scope: document.body,
    
    // Application Constructor
    initialize: function() {
        this.insertPages();
        this.findDimensions();
        this.preloadContent();
        this.bindEvents();
        $('.reflection-response').each(function() {
            $(this).validate({submitHandler: app.submitReply});
        });
        $('.reflection-captcha').each(function() {
            $(this).validate({submitHandler: app.submitCaptcha});
        });
    },
    
    insertPages: function() {
        var casusTemplate = _.template($('#casus-format').html());
        var reflectionTemplate = _.template($('#reflection-format').html());
        $(casusTemplate({
            pageid: 'plate',
            back: 'Doordenkertjes'
        })).appendTo(app.scope).page();
        $(casusTemplate({
            pageid: 'plate-archive-item',
            back: 'Archief'
        })).appendTo(app.scope).page();
        $(reflectionTemplate({
            pageid: 'mirror',
            back: 'Doordenkertjes',
            suffix: ''
        })).appendTo(app.scope).page();
        $(reflectionTemplate({
            pageid: 'mirror-archive-item',
            back: 'Archief',
            suffix: '-2'
        })).appendTo(app.scope).page();
    },
    
    findDimensions: function() {
        this.viewport = {
            width: window.innerWidth,
            height: window.innerHeight,
            pixelRatio: window.devicePixelRatio
        };
        if (this.viewport.width > this.viewport.height) {
            var temp = this.viewport.width;
            this.viewport.width = this.viewport.height;
            this.viewport.height = temp;
        }
    },
    
    preloadContent: function() {
        $.get('/reflection/').done(function(data) {
            app.loadReflection($('#mirror'), data);
        });
        $.get('/tips/').done(app.loadTips);
        $.get('/case/archive').done(app.loadCasusArchive);
        $.get('/reflection/archive').done(app.loadReflectionArchive);
    },
    
    loadCasus: function(page, data) {
        app.current_casus = data.id;
        localStorage.setItem('case_data_' + data.id, JSON.stringify(data));
        page.find('.week-number').html(data.week);
        page.find('.case-text').html(data.text);
        page.find('.case-proposition').html(data.proposition);
        var display = page.find('.case-display');
        display.empty();
        var image_size = Math.ceil((Math.min(500, app.viewport.width) - 20) * app.viewport.pixelRatio);
        var img = $('<img>')
            .attr('src', '/media/' + data.picture + '/' + image_size)
            .load(function() {
                display.append(img);
            });
        if (app.viewport.pixelRatio != 1) {
            // The pageshow event is deprecated as of JQM 1.4.0 and will be
            // removed in JQM 1.6.0. However, at this time no suitable
            // alternative is available. If there is still no suitable
            // alternative by that time, we can emply the technique described
            // here: 
            // http://viralpatel.net/blogs/jquery-trigger-custom-event-show-hide-element/
            page.one('pageshow', function() {
                img.width(img.width() / app.viewport.pixelRatio);
            });
        }
        page.css('background-color', data.background || '#f9f9f9');
        if (localStorage.getItem('has_voted_' + data.id) ||
                data.closure && new Date(data.closure) <= new Date()) {
            app.displayVotes(page);
        } else {
            app.displayVoteButtons(page);
        }
    },
    
    loadReflection: function(page, data) {
        if (data.token) localStorage.setItem('token', data.token);
        app.current_reflection = data.id;
        localStorage.setItem('reflection_data_' + data.id, JSON.stringify(data));
        localStorage.setItem('last_retrieve', data.since);
        page.find('.week-number').html(data.week);
        page.find('.reflection-text').html(data.text);
        page.find('.reflection-discussion').empty();
        _.each(data.responses, function(datum) {
            app.appendReply(page, datum);
        });
        var nickname = localStorage.getItem('nickname');
        if (nickname) page.find('[name="p"]').val(nickname);
        if (data.closure) {
            if (new Date(data.closure) <= new Date()) {
                page.find('.reflection-response').hide();
                page.find('.reflection-closure-announce').hide();
            } else {
                page.find('.reflection-closure-date').text(data.closure);
                page.find('.reflection-closed-notice').hide();
            }
        } else {
            page.find('.reflection-closed-notice').hide();
            page.find('.reflection-closure-announce').hide();
        }
    },
    
    renderTip: function(data) {
        var item = $('<li>');
        var tip = item;
        if (data.href) {
            tip = $('<a>').attr('href', data.href).attr('target', '_blank');
            tip.appendTo(item);
        }
        $('<h3>').html(data.title).css('white-space', 'normal').appendTo(tip);
        if (data.author) $('<p>').html(data.author).appendTo(tip);
        if (data.text) $('<p>').html(data.text).appendTo(tip);
        return item;
    },
    
    loadTips: function(data) {
        // Load labour code tips
        $("#labour-code-tips").append(_.map(data.labour, app.renderTip));
        // Load website links
        $("#website-links").append(_.map(data.site, app.renderTip));
        // Load book tips
        $("#book-tips").append(_.map(data.book, app.renderTip));
        // We need to refresh the listviews on load.
        $('.tips-list').listview('refresh');
    },
    
    loadCasusArchive: function(data) {
        app.loadCasus($('#plate'), data.all[0]);
        app.renderArchiveList(data.all, $('#plate-archive-list'), function(ev) {
            var id = $(ev.target).data('identifier');
            $.get('/case/' + id).done(function(data) {
                app.loadCasus($('#plate-archive-item'), data);
            });
        });
    },
    
    loadReflectionArchive: function(data) {
        app.renderArchiveList(data.all, $('#mirror-archive-list'), function(ev) {
            var id = $(ev.target).data('identifier');
            $.get('/reflection/' + id + '/').done(function(data) {
                app.loadReflection($('#mirror-archive-item'), data);
            });
        });
    },
    
    renderArchiveList: function(data, listElem, retrieve) {
        var item, anchor;
        var target = '#' + listElem.prop('id').slice(0, -4) + 'item';
        _.each(data, function(datum) {
            item = $('<li>');
            anchor = $('<a>').attr('href', target).text(datum.title)
                             .data('identifier', datum.id).click(retrieve)
                             .appendTo(item);
            $('<span>').addClass('week-number ui-li-count')
                       .text(datum.week).appendTo(anchor);
            listElem.append(item);
        });
        listElem.listview('refresh');        
    },
    
    submitVote: function(target, choice) {
        var id = app.current_casus,
            case_data = JSON.parse(localStorage.getItem('case_data_' + id)),
            page = $(target).parent();
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
                    app.displayVotes(page);
                }
            });
        }
    },
    
    submitReply: function(form) {
        form = $(form);
        form.hide();
        var page = form.parent(),
            id = app.current_reflection,
            reflection_data = JSON.parse(localStorage.getItem('reflection_data_' + id)),
            nickname = form.find('[name="p"]').val(),
            message = form.find('[name="r"]').val();
        localStorage.setItem('nickname', nickname);
        $.post('/reflection/' + id + '/reply', {
            p: nickname,
            r: message,
            t: localStorage.getItem('token'),
            'last-retrieve': localStorage.getItem('last_retrieve'),
            ca: page.find('[name="ca"]').val()
        }).done(function(data) {
            localStorage.setItem('token', data.token);
            switch (data.status) {
            case 'success':
                app.appendReply(page, {
                    pseudonym: nickname,
                    'message': message
                });
                form.find('[name="r"]').val('');
                form.show();
                break;
            case 'ninja':
                page.find('.ninja-message').popup('open', {positionTo: 'window'});
                page.find('.reply-submitted').remove();
                _.each(data.new, function(datum) {
                    app.appendReply(page, datum);
                });
                form.show();
                localStorage.setItem('last_retrieve', data.since);
                break;
            case 'captcha':
                page.find('.captcha-challenge').text(data.captcha_challenge);
                page.find('.captcha-popup').popup('open', {positionTo: 'window'});
            }
        }).fail(function(jqXHR) {
            if ( jqXHR.status == 400 &&
                 jqXHR.responseText && jqXHR.responseText[0] == '{' ) {
                var data = JSON.parse(jqXHR.responseText);
                localStorage.setItem('token', data.token);
                switch (data.status) {
                case 'closed':
                    page.find('.reflection-closed-popup').popup('open', {positionTo: 'window'});
                    page.find('.reflection-closure-announce').hide();
                    page.find('.reflection-closed-notice').show();
                    break;
                case 'invalid':
                    page.find('.reflection-invalid-popup').popup('open', {positionTo: 'window'});
                    page.find('.reflection-response').show();
                }
            }
        });
    },
    
    submitCaptcha: function(form) {
        var page = $(form).parents('[data-role="page"]');
        page.find('.captcha-popup').popup('close');
        app.submitReply(page.find('.reflection-response'));
        $(form).find('[name="ca"]').val('');
    },
    
    appendReply: function(page, data) {
        var upvotes = data.up || 0,
            downvotes = data.down || 0,
            score = app.getScore(upvotes, downvotes);
        var div = $('<div></div>');
        div.addClass('reply-' + (data.id || 'submitted'));
        var date = '<span class="reply-date">' + (data.submission || 'net') + '</span>';
        var pseudonym = '<span class="reply-nick">' + data.pseudonym + '</span>';
        var synopsis = $('<h3 class="reply-synopsis"></h3>').append(date + ' ' + pseudonym);
        div.append(synopsis);
        div.append(date);
        div.append(pseudonym);
        div.append($('<span class="reply-content"></span>').html(data.message));
        if (data.id) {
            div.append('<br>');
            div.append($('<a href="#">leerzaam</a>')
                        .addClass('reply-vote ui-btn ui-icon-plus ui-btn-icon-left')
                        .data('for', data.id)
                        .click(function() {
                            app.submitReplyVote(data.id, 'up');
                        }));
            div.append($('<a href="#">ongewenst</a>')
                        .addClass('reply-vote ui-btn ui-icon-minus ui-btn-icon-right')
                        .data('for', data.id)
                        .click(function() {
                            app.submitReplyVote(data.id, 'down');
                        }));
        }
        page.find('.reflection-discussion').append(div);

        // If score is lower than treshold, show the synopsis and display as collapsible.
        if (score < 0.35) {
            synopsis.show();
            page.find('.reply-' + data.id + ' .reply-synopsis .reply-nick').html('spam');
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
                    $('.reply-' + id + ' .reply-vote').hide();
                    $('.reply-' + id + ' .reply-vote:last')
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
    
    displayVotes: function(page) {
        var id = app.current_casus,
            case_data = JSON.parse(localStorage.getItem('case_data_' + id)),
            yes_count = case_data.yes,
            no_count = case_data.no;
        page.children('a').hide();
        page.find('.yes_count').html('ja ' + yes_count).show();
        page.find('.no_count').html(no_count + ' nee').show();
        page.find('.no_bar').width(app.viewport.width - 15 * 8).show();
        page.find('.yes_bar').css('width', 100 * yes_count / (yes_count + no_count) + '%').show();
    },
    
    displayVoteButtons: function(page) {
        page.children('a').show();
        page.find('.yes_count, .no_count, .no_bar, .yes_bar').hide();
    },
    
    // Bind Event Listeners
    // Bind any events that are required on startup. Common events are:
    // 'load', 'deviceready', 'offline', and 'online'.
    bindEvents: function() {
        $('.vote-btn-yes').on('mousedown touchstart', function(event) {
            app.submitVote(event.target, 'yes');
        });
        $('.vote-btn-no').on('mousedown touchstart', function(event) {
            app.submitVote(event.target, 'no');
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
