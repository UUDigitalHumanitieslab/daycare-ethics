/*
    (c) 2014, 2015 Digital Humanities Lab, Utrecht University
    Authors: Julian Gonggrijp, Martijn van der Klis
*/

'use strict';

// ConnectivityFsm is based directly on the example from machina-js.org.
// Most important difference is that checkHeartbeat is simply a member
// of the state machine itself.
var ConnectivityFsm = machina.Fsm.extend({
    namespace: 'connectivity',

    initialState: 'probing',
    
    requestData: {
        url: 'ping',
        method: 'HEAD',
        timeout: 5000
    },

    checkHeartbeat: function() {
        var self = this;
        self.emit('checking-heartbeat');
        $.ajax(self.requestData).done(function() {
            self.emit('heartbeat');
        }).fail(function() {
            self.emit('no-heartbeat');
        });
    },

    initialize: function() {
        var self = this;
        self.on('heartbeat', function() {
            self.handle('heartbeat');
        });
        self.on('no-heartbeat', function() {
            self.handle('no-heartbeat');
        });
        $(window).bind('online', function() {
            self.handle('window.online');
        });
        $(window).bind( 'offline', function() {
            self.handle('window.offline');
        });
        $(window.applicationCache).bind('error', function() {
            self.handle('appCache.error');
        });
        $(window.applicationCache).bind('downloading', function() {
            self.handle('appCache.downloading');
        });
        $(document).on('resume', function () {
            self.handle('device.resume');
        });
        if (self.origin) self.requestData = _.create(self.requestData, {
            url: self.origin + self.requestData.url
        });
    },

    states: {
        probing: {
            _onEnter: function() {
                this.checkHeartbeat();
            },
            'heartbeat': 'online',
            'no-heartbeat': 'disconnected',
        },
        online: {
            'window.offline': 'probing',
            'appCache.error': 'probing',
            'request.timeout': 'probing',
            'device.resume': 'probing',
        },
        disconnected: {
            'window.online': 'probing',
            'appCache.downloading': 'probing',
            'device.resume': 'probing',
        }
    }
});

// Manage the content and interactivity of a page that depends on connectivity.
// When instantiating, provide at least the keys `namespace`, `url`, `page`
// and `archive`. You probably need to override `display`. Optionally also
// override the other member functions.
var PageFsm = machina.Fsm.extend({
    initialState: 'empty',
    initialize: function() {
        var self = this;
        this.initHook();
        app.connectivity.on('heartbeat', function() {
            self.handle('online');
        });
        app.connectivity.on('no-heartbeat', function() {
            self.handle('disconnected');
        });
        if (app.connectivity.state !== 'probing') {
            self.handle(app.connectivity.state);
        }
    },
    initHook: function() {},
    fetch: function() {
        return $.get(this.url);
    },
    load: function() {
        var data = localStorage.getItem(this.archive);
        if (!data) return false;
        return JSON.parse(data);
    },
    store: function(data) {
        localStorage.setItem(this.archive, JSON.stringify(data));
        this.emit('stored');
    },
    display: function(data) {},
    cycle: function(data) {
        this.display(data);
        this.store(data);
    },
    activate: function() {
        this.page.find('.disconnected').hide();
        this.page.find('.online').show();
    },
    deactivate: function() {
        this.page.find('.online').hide();
        this.page.find('.disconnected').show();
    },
    states: {
        empty: {
            online: 'active',
            disconnected: 'archived'
        },
        archived: {
            _onEnter: function() {
                var archive = this.load();
                if (archive) this.display(archive);
                this.deactivate();
            },
            online: 'active'
        },
        active: {
            _onEnter: function() {
                this.fetch().done(_.bind(this.cycle, this));
                this.activate();
            },
            disconnected: 'inactive'
        },
        inactive: {
            _onEnter: function() {
                this.deactivate();
            },
            online: 'active'
        }
    }
});

var ReflectionFsm = PageFsm.extend({
    is_open: true,
    initHook: function() {
        this.page.find('.reflection-response')
            .validate({submitHandler: _.bind(app.submitReply, this)});
        this.page.find('.reflection-captcha')
            .validate({submitHandler: _.bind(app.submitCaptcha, this)});
    },
    load: function() {
        var fulltext = localStorage.getItem(this.archive);
        var list = localStorage.getItem('reflection_list');
        return JSON.parse(fulltext) ||
               list && _.findWhere(JSON.parse(list).all, {id: this.id});
    },
    cycle: function(data) {
        this.data = data;
        this.display(data);
        this.store(data);
    },
    update: function(since, newresponses) {
        _.assign(this.data, {
            since: since,
            responses: this.data.responses.concat(newresponses)
        });
        this.store(this.data);
    },
    display: function(data) {
        var self = this;
        this.id = data.id;
        this.page.find('.week-number').html(data.week);
        this.page.find('.reflection-text').html(data.text);
        this.page.find('.reflection-discussion').empty();
        _.each(data.responses, function(datum) {
            app.appendReply(self.page, datum);
        });
        var nickname = localStorage.getItem('nickname');
        if (nickname) this.page.find('[name="p"]').val(nickname);
        if (data.closure) {
            if (new Date(data.closure) <= new Date()) {
                this.page.find('.reflection-response').hide();
                this.page.find('.reflection-closure-announce').hide();
                this.is_open = false;
            } else {
                this.page.find('.reflection-closure-date').text(data.closure);
                this.page.find('.reflection-closed-notice').hide();
            }
        } else {
            this.page.find('.reflection-closed-notice').hide();
            this.page.find('.reflection-closure-announce').hide();
        }
    }
});

var CurrentReflectionFsm = ReflectionFsm.extend({
    fetch: function() {
        var data = {};
        var token = localStorage.getItem('token');
        if (token) data.t = token;
        return $.get(app.base + 'reflection/', data);
    },
    load: function() {
        var id = localStorage.getItem('latest_reflection');
        if (!id) return false;
        this.archive = 'reflection_data_' + id;
        this.data = JSON.parse(localStorage.getItem(this.archive));
        return this.data;
    },
    store: function(data) {
        localStorage.setItem('latest_reflection', data.id);
        this.archive = 'reflection_data_' + data.id;
        localStorage.setItem(this.archive, JSON.stringify(data));
    },
    cycle: function(data) {
        if (data.token) {
            localStorage.setItem('token', data.token);
            delete data.token;
        }
        this.data = data;
        this.display(data);
        this.store(data);
    }
});

// CasusFsm is a bit different because it relies on app.casusListFsm for
// data retrieval.
var CasusFsm = machina.Fsm.extend({
    archive: 'casus_list',
    initialState: 'inactive',
    initialize: function() {
        this.page.children('a').data('fsm', this);
        if (app.casusListFsm.state !== 'empty') {
            this.refresh();
        }
        var handler = _.bind(this.refresh, this);
        app.casusListFsm.on('handled', handler);
        app.casusListFsm.on('stored', handler);
    },
    refresh: function() {
        this.data = this.load();
        if (! this.data) return;
        this.id = this.data.id;
        this.display(this.data);
        if (
            localStorage.getItem('has_voted_' + this.id) ||
            this.data.closure && new Date(this.data.closure) <= new Date()
        ) {
            this.close();
        } else {
            this.handle(app.casusListFsm.state);
        }
    },
    load: function() {
        var list = localStorage.getItem(this.archive);
        if (this.id) {
            return list && _.findWhere(JSON.parse(list).all, {id: this.id});
        } else {
            return list && JSON.parse(list).all[0];
        }
    },
    store: function(data) {
        var list = localStorage.getItem(this.archive);
        var archive = list && JSON.parse(list) || {all: []};
        var index = _.findIndex(archive.all, {id: this.id});
        if (index >= 0) {
            archive.all[index] = data;
        } else {
            archive.all.push(data);
        }
        localStorage.setItem(this.archive, JSON.stringify(archive));
    },
    close: function() {
        this.handle('close');
    },
    display: function(data) {
        this.page.find('.week-number').html(data.week);
        this.page.find('.case-text').html(data.text);
        this.page.find('.case-proposition').html(data.proposition);
        this.page.css('background-color', data.background || '#f9f9f9');
        if (this.imageHandler) return;
        var self = this;
        if (app.connectivity.state === 'online') {
            this.insertImage(data);
            this.imageHandler = true;
        } else {
            this.imageHandler = app.connectivity.on('heartbeat', function() {
                self.insertImage(data);
                self.imageHandler.off();
            });
            this.page.find('.case-display').empty().html(
                '<p>afbeelding verschijnt wanneer je<br>' +
                'verbinding maakt met internet</p>'
            );
        }
    },
    insertImage: function(data) {
        var display = this.page.find('.case-display');
        display.empty();
        var image_size = Math.ceil((Math.min(500, app.viewport.width) - 20) * app.viewport.pixelRatio);
        var img = $('<img>')
            .attr('src', app.base + 'media/' + data.picture + '/' + image_size)
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
            this.page.one('pageshow', function() {
                img.width(img.width() / app.viewport.pixelRatio);
            });
        }
    },
    displayVotes: function() {
        if (! this.data) return;
        var yes_count = this.data.yes,
            no_count = this.data.no;
        this.page.find('.yes_count').html('ja ' + yes_count).show();
        this.page.find('.no_count').html(no_count + ' nee').show();
        this.page.find('.no_bar').width(app.viewport.width - 15 * 8).show();
        this.page.find('.yes_bar').css('width', 100 * yes_count / (yes_count + no_count) + '%').show();
    },
    displayVoteButtons: function() {
        this.page.children('a').show();
    },
    hideVotes: function() {
        this.page.find('.yes_count, .no_count, .no_bar, .yes_bar').hide();
    },
    hideVoteButtons: function() {
        this.page.children('a').hide();
    },
    states: {
        inactive: {
            _onEnter: function() {
                this.hideVotes();
                this.hideVoteButtons();
            },
            active: 'active',
            close: 'closed'
        },
        active: {
            _onEnter: function() {
                this.hideVotes();
                this.displayVoteButtons();
            },
            inactive: 'inactive',
            archived: 'inactive',
            close: 'closed'
        },
        closed: {
            _onEnter: function() {
                this.hideVoteButtons();
                this.displayVotes();
            },
        }
    }
});

// The app object contains the core logic of the client side.
var app = {
    scope: document.body,
    origin: '',
    
    // Application Constructor
    initialize: function() {
        this.detectBase();
        this.connectivity = new ConnectivityFsm({origin: this.base});
        this.insertPages();
        this.findDimensions();
        this.preloadContent();
        this.bindEvents();
    },
    
    detectBase: function() {
        this.base = window.location.protocol === 'file:' && this.origin || '';
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
        app.currentReflectionFsm = new CurrentReflectionFsm({
            namespace: 'currentReflectionFsm',
            url: app.base + 'reflection/',
            page: $('#mirror')
        });
        app.reflectionListFsm = new PageFsm({
            namespace: 'reflectionListFsm',
            url: app.base + 'reflection/archive',
            page: $('#mirror-archive'),
            archive: 'reflection_list',
            display: app.loadReflectionArchive
        });
        app.tipsFsm = new PageFsm({
            namespace: 'tipsFsm',
            url: app.base + 'tips/',
            page: $('#links-tips'),
            archive: 'tips',
            display: app.loadTips
        });
        app.casusListFsm = new PageFsm({
            namespace: 'casusListFsm',
            url: app.base + 'case/archive',
            page: $('#plate-archive'),
            archive: 'casus_list',
            display: app.loadCasusArchive
        });
        app.currentCasusFsm = new CasusFsm({
            namespace: 'currentCasusFsm',
            page: $('#plate'),
        });
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
        $("#labour-code-tips").empty().append(_.map(data.labour, app.renderTip));
        // Load website links
        $("#website-links").empty().append(_.map(data.site, app.renderTip));
        // Load book tips
        $("#book-tips").empty().append(_.map(data.book, app.renderTip));
        // We need to refresh the listviews on load.
        $('.tips-list').listview();
        $('.tips-list').listview('refresh');
        app.catchExternalLinks($('#links-tips'));
    },
    
    loadCasusArchive: function(data) {
        app.renderArchiveList(
            data.all,
            $('#plate-archive-list'),
            app.archivedCasusHandler
        );
    },
    
    archivedCasusHandler: function(ev) {
        var id = $(ev.target).data('identifier');
        if (app.oldCasusFsm && app.oldCasusFsm.id === id) return;
        // the next statement deletes the former app.oldReflectionFsm (if any)
        app.oldCasusFsm = new CasusFsm({
            namespace: 'oldCasusFsm_' + id,
            page: $('#plate-archive-item'),
            id: id
        });
    },
    
    loadReflectionArchive: function(data) {
        app.renderArchiveList(
            data.all,
            $('#mirror-archive-list'),
            app.archivedReflectionHandler
        );
    },
    
    archivedReflectionHandler: function(ev) {
        var id = $(ev.target).data('identifier');
        if (app.oldReflectionFsm && app.oldReflectionFsm.id === id) return;
        // the next statement deletes the former app.oldReflectionFsm (if any)
        app.oldReflectionFsm = new ReflectionFsm({
            namespace: 'oldReflectionFsm_' + id,
            url: app.base + 'reflection/' + id + '/',
            page: $('#mirror-archive-item'),
            archive: 'reflection_data_' + id,
            id: id
        });
    },
    
    renderArchiveList: function(data, listElem, retrieve) {
        var item, anchor;
        var target = '#' + listElem.prop('id').slice(0, -4) + 'item';
        listElem.empty();
        _.each(data, function(datum) {
            item = $('<li>');
            anchor = $('<a>').attr('href', target).text(datum.title)
                             .data('identifier', datum.id).click(retrieve)
                             .appendTo(item);
            $('<span>').addClass('week-number ui-li-count')
                       .text(datum.week).appendTo(anchor);
            listElem.append(item);
        });
        listElem.listview();        
        listElem.listview('refresh');        
    },
    
    submitVote: function(target, choice) {
        var fsm = $(target).data('fsm');
        if (localStorage.getItem('has_voted_' + fsm.id)) return;
        if (choice === 'yes' || choice === 'no') {
            $.post(app.base + 'case/vote', {
                'id': fsm.id,
                'choice': choice,
                't': localStorage.getItem('token')
            }).done(function(data) {
                localStorage.setItem('token', data.token);
                if (data.status === 'success') {
                    fsm.data[choice] += 1;
                    fsm.store(fsm.data);
                    localStorage.setItem('has_voted_' + fsm.id, true);
                    fsm.close();
                }
            });
        }
    },
    
    // bound to the reflection FSM when called
    submitReply: function(form) {
        form = $(form);
        form.hide();
        var fsm = this,
            nickname = form.find('[name="p"]').val(),
            message = form.find('[name="r"]').val();
        localStorage.setItem('nickname', nickname);
        $.post(app.base + 'reflection/' + fsm.id + '/reply', {
            p: nickname,
            r: message,
            t: localStorage.getItem('token'),
            'last-retrieve': fsm.data.since,
            ca: fsm.page.find('[name="ca"]').val()
        }).done(function(data) {
            localStorage.setItem('token', data.token);
            switch (data.status) {
            case 'success':
                _.each(data.new, function(datum) {
                    app.appendReply(fsm.page, datum);
                });
                form.find('[name="r"]').val('');
                form.show();
                fsm.update(data.since, data.new);
                break;
            case 'ninja':
                fsm.page.find('.ninja-message').popup('open', {positionTo: 'window'});
                _.each(data.new, function(datum) {
                    app.appendReply(fsm.page, datum);
                });
                form.show();
                fsm.update(data.since, data.new);
                break;
            case 'captcha':
                fsm.page.find('.captcha-challenge').text(data.captcha_challenge);
                fsm.page.find('.captcha-popup').popup('open', {positionTo: 'window'});
                fsm.update(data.since, []);
            }
        }).fail(function(jqXHR) {
            if ( jqXHR.status == 400 &&
                 jqXHR.responseText && jqXHR.responseText[0] == '{' ) {
                var data = JSON.parse(jqXHR.responseText);
                localStorage.setItem('token', data.token);
                switch (data.status) {
                case 'closed':
                    fsm.page.find('.reflection-closed-popup').popup('open', {positionTo: 'window'});
                    fsm.page.find('.reflection-closure-announce').hide();
                    fsm.page.find('.reflection-closed-notice').show();
                    break;
                case 'invalid':
                    fsm.page.find('.reflection-invalid-popup').popup('open', {positionTo: 'window'});
                    fsm.page.find('.reflection-response').show();
                }
            }
        });
    },
    
    // bound to the reflection FSM when called
    submitCaptcha: function(form) {
        var page = this.page;
        page.find('.captcha-popup').popup('close');
        _.bind(app.submitReply, this)(page.find('.reflection-response'));
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
                        .addClass('reply-vote online ui-btn ui-icon-plus ui-btn-icon-left')
                        .data('for', data.id)
                        .click(function() {
                            app.submitReplyVote(data.id, 'up');
                        }));
            div.append($('<a href="#">ongewenst</a>')
                        .addClass('reply-vote online ui-btn ui-icon-minus ui-btn-icon-right')
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
            $.post(app.base + 'reply/' + id + '/moderate/', {
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
    
    catchExternalLinks: function(element) {
        element.find('a[target="_blank"]').click(function(event) {
            event.preventDefault();
            window.open(this.href, '_blank');
        });
    },
    
    openInExternalApp: function(event) {
        event.preventDefault();
        cordova.plugins.disusered.open(event.target.href);
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
        app.catchExternalLinks($('#about'));
        window.open = cordova.InAppBrowser.open;
        $('#shelf a[target="_blank"], #about a[href^="mailto:"]')
            .click(app.openInExternalApp);
    },
    
    // Update DOM on a Received Event
    receivedEvent: function(id) {
    }
};
