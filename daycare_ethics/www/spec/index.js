/*
    (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
    Author: Julian Gonggrijp, j.gonggrijp@uu.nl
*/
describe('app', function() {
    var fakeLatestCaseData = {
        'id': 1,
        'title': 'testcasus',
        'publication': '2015-03-02',
        'week': '10',
        'closure': null,
        'text': 'some dummy text',
        'proposition': 'difficult question',
        'picture': null,
        'background': '#998877'
    };
    var fakeReflectionData = {
        'token': 'abcdefghijk',
        'id': 2,
        'title': 'testreflection',
        'publication': '2015-03-02',
        'week': '10',
        'closure': null,
        'text': 'some dummy text',
        'responses': [
            {
                'id': 1,
                'up': 0,
                'down': 15,
                'submission': '2015-03-02',
                'pseudonym': 'malbolge',
                'message': '&lt;script&gt;wreakHavoc();&lt;/script&gt;'
            },
            {
                'id': 2,
                'up': 1,
                'down': 10,
                'submission': '2015-03-03',
                'pseudonym': 'victim',
                'message': 'help me'
            }
        ]
    };
    
    beforeEach(function() {
        app.scope = $('#stage');
        jasmine.Ajax.install();
    });
    
    afterEach(function() {
        jasmine.Ajax.uninstall();
        localStorage.clear();
    });
    
    describe('initialize', function() {
        var emulateDeviceReady = function(callback) {
            app.initialize();
            helper.trigger(window.document, 'deviceready');
            callback();
        };
        beforeEach(function(done) {
            spyOn(app, 'insertPages').and.callThrough();
            spyOn(app, 'findDimensions').and.callThrough();
            spyOn(app, 'onDeviceReady');
            spyOn(app, 'preloadContent');
            emulateDeviceReady(done);
        });
        it('should call four other functions', function() {
            expect(app.insertPages).toHaveBeenCalled();
            expect(app.findDimensions).toHaveBeenCalled();
            expect(app.preloadContent).toHaveBeenCalled();
            expect(app.onDeviceReady).toHaveBeenCalled();
        });
        it('should validate the forms', function() {
            expect($('#stage').find('.reflection-response, .reflection-captcha').find('[aria-required]').length).toBe(6);
        });
    });
    
    describe('insertPages', function() {
        it('creates pages from a template', function() {
            app.insertPages();
            expect($('#plate')).toBeInDOM();
            expect($('#plate-archive-item')).toBeInDOM();
            expect($('#mirror')).toBeInDOM();
            expect($('#mirror-archive-item')).toBeInDOM();
        });
    });
    
    describe('findDimensions', function() {
        beforeEach(function() {
            app.findDimensions();
        });
        it('sets viewport dimensions on the app object', function() {
            expect(app.viewport).toBeDefined();
            expect(app.viewport.width).toEqual(jasmine.any(Number));
            expect(app.viewport.height).toEqual(jasmine.any(Number));
            expect(app.viewport.pixelRatio).toEqual(jasmine.any(Number));
        });
        it('should find realistic values', function() {
            expect(app.viewport.width).toBe(Math.floor(app.viewport.width));
            expect(app.viewport.width).toBeGreaterThan(300);
            expect(app.viewport.width).toBeLessThan(4000);
            expect(app.viewport.height).toBe(Math.floor(app.viewport.height));
            expect(app.viewport.height).toBeGreaterThan(400);
            expect(app.viewport.height).toBeLessThan(2500);
            expect(app.viewport.pixelRatio).not.toBeLessThan(1);
            expect(app.viewport.pixelRatio).not.toBeGreaterThan(3);
        });
        it('will assume that the shortest dimension is the width', function() {
            expect(app.viewport.width).not.toBeGreaterThan(app.viewport.height);
        });
    });
    
    describe('preloadContent', function() {
        xit('fetches data from the server and passes them to other functions', function() {
            spyOn(app, 'loadReflection');
            spyOn(app, 'loadTips');
            spyOn(app, 'loadCasusArchive');
            spyOn(app, 'loadReflectionArchive');
            app.preloadContent();
            var requests = jasmine.Ajax.requests;
            expect(requests.count()).toBe(4);
            expect(requests.at(0).url).toBe('/reflection/');
            expect(requests.at(1).url).toBe('/tips/');
            expect(requests.at(2).url).toBe('/case/archive');
            expect(requests.at(3).url).toBe('/reflection/archive');
            requests.at(0).respondWith({responseText: ''});
            requests.at(1).respondWith({responseText: ''});
            requests.at(2).respondWith({responseText: ''});
            requests.at(3).respondWith({responseText: ''});
            expect(app.loadReflection).toHaveBeenCalled();
            expect(app.loadTips).toHaveBeenCalled();
            expect(app.loadCasusArchive).toHaveBeenCalled();
            expect(app.loadReflectionArchive).toHaveBeenCalled();
            
        });
    });
    
    describe('loadCasus', function() {
        beforeEach(function() {
            app.insertPages();
        });
        it('populates a page with casus data', function() {
            app.loadCasus($('#plate'), fakeLatestCaseData);
            expect($('#plate .week-number')).toContainText('10');
            expect($('#plate .case-text')).toContainText('some dummy text');
            expect($('#plate .case-proposition')).toContainText('difficult question');
            expect($('#plate')).toHaveCss({'background-color': 'rgb(153, 136, 119)'});
        });
        it('displays the votes if the user voted before', function() {
            localStorage.setItem('has_voted_1', true);
            spyOn(app, 'displayVotes');
            app.loadCasus($('#plate'), fakeLatestCaseData);
            expect(app.displayVotes).toHaveBeenCalled();
        });
        it('provides voting buttons otherwise', function() {
            spyOn(app, 'displayVoteButtons');
            app.loadCasus($('#plate'), fakeLatestCaseData);
            expect(app.displayVoteButtons).toHaveBeenCalled();
        });
    });
    
    describe('loadReflection', function() {
        beforeEach(function() {
            app.insertPages();
            this.date = $.now();
        });
        it('populates a page with reflection data', function() {
            spyOn(app, 'appendReply').and.callThrough();
            app.loadReflection($('#mirror'), fakeReflectionData);
            expect($('#mirror .week-number')).toContainText('10');
            expect($('#mirror .reflection-text')).toContainText('some dummy text');
            expect(app.appendReply.calls.count()).toBe(2);
            expect($('#mirror .reflection-discussion > *')).toHaveLength(2);
            $('#stage, #mirror').show();
            expect($('#mirror .reflection-response')).toBeVisible();
            expect($('#mirror .reflection-closed-notice')).toBeHidden();
            expect($('#mirror .reflection-closure-announce')).toBeHidden();
        });
        it('sets the token if provided', function() {
            app.loadReflection($('#mirror'), fakeReflectionData);
            expect(localStorage.getItem('token')).toBe('abcdefghijk');
        });
        it('warns the user if a closure date is set', function() {
            this.date += 24 * 60 * 60 * 1000; // one day ahead
            var date = (new Date(this.date)).toISOString().slice(0, 10)
            var customFakeData = _(fakeReflectionData).clone();
            customFakeData.closure = date;
            app.loadReflection($('#mirror'), customFakeData);
            $('#stage, #mirror').show();
            expect($('#mirror .reflection-response')).toBeVisible();
            expect($('#mirror .reflection-closed-notice')).toBeHidden();
            expect($('#mirror .reflection-closure-announce')).toBeVisible();
            expect($('#mirror .reflection-closure-date')).toContainText(date);
        });
        it('warns the user when replying is no longer possible', function() {
            this.date -= 24 * 60 * 60 * 1000; // one day prior
            var date = (new Date(this.date)).toISOString().slice(0, 10)
            var customFakeData = _(fakeReflectionData).clone();
            customFakeData.closure = date;
            app.loadReflection($('#mirror'), customFakeData);
            $('#stage, #mirror').show();
            expect($('#mirror .reflection-response')).toBeHidden();
            expect($('#mirror .reflection-closed-notice')).toBeVisible();
            expect($('#mirror .reflection-closure-announce')).toBeHidden();
        });
    });
    
    describe('loadTips', function() {
        beforeEach(function() {
            $(_.template($('#tips-format').html(), {})).appendTo('#stage').page();
            app.loadTips({
                'labour': [
                    { 'title': 'labourtest1' },
                    { 'title': 'labourtest2' }
                ],
                'site': [
                    {
                        'href': 'http://www.example.com',
                        'title': 'sitetest'
                    }
                ],
                'book': [
                    {
                        'title': 'interesting book',
                        'author': 'interesting author'
                    },
                    {
                        'title': 'amusing book',
                        'author': 'amusing author'
                    },
                    {
                        'title': 'annoying book',
                        'author': 'annoying author'
                    }
                ]
            });
        });
        it('inserts labour code tips in the first list', function() {
            var items = $('#labour-code-tips > *');
            expect(items).toHaveLength(2);
            expect(items[0].outerHTML).toBe('<li class="ui-li-static ui-body-inherit ui-first-child">labourtest1</li>');
        });
        it('inserts website tips in the second list', function() {
            var items = $('#website-links > *');
            expect(items).toHaveLength(1);
            expect(items[0].outerHTML).toBe('<li class="ui-first-child ui-last-child"><a href="http://www.example.com" target="_blank" class="ui-btn ui-btn-icon-right ui-icon-carat-r">sitetest</a></li>');
        });
        it('inserts book tips in the third list', function() {
            var items = $('#book-tips > *');
            expect(items).toHaveLength(3);
            expect(items[2].outerHTML).toBe('<li class="ui-li-static ui-body-inherit ui-last-child"><h3 style="white-space: normal;">annoying book</h3><p>annoying author</p></li>');
        });
    });
    
    describe('loadCasusArchive', function() {
        beforeEach(function() {
            $(_.template($('#casus-archive-format').html(), {}))
                .appendTo('#stage').page();
            var fakeData = { 'all': [
                _.clone(fakeLatestCaseData),
                fakeLatestCaseData
            ]};
            _.assign(fakeData.all[0], { 'id': 2, 'week': '11' });
            spyOn(app, 'loadCasus');
            spyOn(app, 'renderArchiveList').and.callThrough();
            app.loadCasusArchive(fakeData);
        });
        it('forwards the most recent casus to loadCasus', function() {
            expect(app.loadCasus).toHaveBeenCalled();
        });
        it('defers to renderArchiveList', function() {
            expect(app.renderArchiveList).toHaveBeenCalled();
        });
        xit('... and installs click handlers to load data', function() {
            $('#plate-archive-list:first-child a').click();
            console.log(jasmine.Ajax.requests);
            expect(jasmine.Ajax.requests.mostRecent().url).toBe('/case/2');
            jasmine.Ajax.requests.mostRecent().respondWith({
                'responseText': ''
            });
            expect(app.loadCasus).toHaveBeenCalled();
        });
    });
    
    describe('loadReflectionArchive', function() {
        beforeEach(function() {
            $(_.template($('#reflection-archive-format').html(), {}))
                .appendTo('#stage').page();
            var fakeData = { 'all': [
                _.clone(fakeReflectionData),
                fakeReflectionData
            ]};
            _.assign(fakeData.all[0], { 'id': 3, 'week': '11' });
            spyOn(app, 'renderArchiveList').and.callThrough();
            app.loadReflectionArchive(fakeData);
        });
        it('defers to renderArchiveList', function() {
            expect(app.renderArchiveList).toHaveBeenCalled();
        });
        xit('... and installs click handlers to load data', function() {
            $('#mirror-archive-list:first-child a').click();
            console.log(jasmine.Ajax.requests);
            expect(jasmine.Ajax.requests.mostRecent().url).toBe('/reflection/3');
            jasmine.Ajax.requests.mostRecent().respondWith({
                'responseText': ''
            });
            expect(app.loadReflection).toHaveBeenCalled();
        });
    });
    
    describe('renderArchiveList', function() {
        beforeEach(function() {
            var fakeData = { 'all': [
                _.clone(fakeReflectionData),
                fakeReflectionData
            ]};
            this.spy = jasmine.createSpy('spy');
            app.insertPages();
            $(_.template($('#reflection-archive-format').html(), {}))
                .appendTo('#stage').page();
            _.assign(fakeData.all[0], { 'id': 3, 'week': '11' });
            app.renderArchiveList(fakeData.all, $('#mirror-archive-list'), this.spy);
        });
        it('creates a list item for each array element passed to it and inserts it into the html element passed to it', function() {
            var items = $('#mirror-archive-list').children();
            var anchors = items.find('a');
            expect(items.length).toBe(2);
            expect($(anchors[0]).data('identifier')).toBe(3);
            expect($(anchors[1]).data('identifier')).toBe(2);
        });
        it('installs whatever click handler was passed to it', function() {
            var anchors = $('#mirror-archive-list').children().find('a');
            $(anchors[0]).click();
            expect(this.spy).toHaveBeenCalled();
            $(anchors[1]).click();
            expect(this.spy.calls.count()).toBe(2);
        });
    });
    
    describe('submitVote', function() {
        beforeEach(function() {
            app.insertPages();
            app.loadCasus($('#plate'), fakeLatestCaseData);
            localStorage.setItem('token', 'qwertyuiop');
            spyOn(app, 'displayVotes');
        });
        it('accepts "yes" votes and displays the results', function() {
            app.submitVote($('#plate .vote-btn-yes'), 'yes');
            var requests = jasmine.Ajax.requests;
            expect(requests.count()).toBe(1);
            var post = requests.at(0);
            expect(post.method).toBe('POST');
            expect(post.url).toBe('/case/vote');
            expect(post.requestHeaders['Content-Type']).toBe('application/x-www-form-urlencoded; charset=UTF-8');
            expect(post.requestHeaders['X-Requested-With']).toBe('XMLHttpRequest');
            expect(post.params).toBe('id=1&choice=yes&t=qwertyuiop');
            post.respondWith({
                'status': 200,
                'responseText': JSON.stringify({
                    'token': '1234567890',
                    'status': 'success'
                }),
                'contentType': 'application/json'
            });
            expect(localStorage.getItem('token')).toBe('1234567890');
            expect(app.displayVotes).toHaveBeenCalledWith($('#plate'));
        });
        it('also accepts "no" votes', function() {
            app.submitVote($('#plate .vote-btn-no'), 'no');
            var requests = jasmine.Ajax.requests;
            expect(requests.count()).toBe(1);
            var post = requests.at(0);
            expect(post.method).toBe('POST');
            expect(post.url).toBe('/case/vote');
            expect(post.requestHeaders['Content-Type']).toBe('application/x-www-form-urlencoded; charset=UTF-8');
            expect(post.requestHeaders['X-Requested-With']).toBe('XMLHttpRequest');
            expect(post.params).toBe('id=1&choice=no&t=qwertyuiop');
        });
        it('remembers that you have voted before', function() {
            expect(localStorage.getItem('has_voted_1')).toBeFalsy();
            app.submitVote($('#plate .vote-btn-yes'), 'yes');
            expect(localStorage.getItem('has_voted_1')).toBeFalsy();
            var requests = jasmine.Ajax.requests;
            expect(requests.count()).toBe(1);
            var post = requests.at(0);
            post.respondWith({
                'status': 200,
                'responseText': JSON.stringify({
                    'token': '1234567890',
                    'status': 'success'
                }),
                'contentType': 'application/json'
            });
            expect(localStorage.getItem('has_voted_1')).toBeTruthy();
            app.submitVote($('#plate .vote-btn-no'), 'no');
            expect(requests.count()).toBe(1);
        });
        it('rejects votes other than "yes" or "no"', function() {
            app.submitVote($('#plate .vote-btn-yes'), 'y');
            app.submitVote($('#plate .vote-btn-yes'), 'n');
            app.submitVote($('#plate .vote-btn-yes'), 'please');
            app.submitVote($('#plate .vote-btn-yes'), 'nope');
            app.submitVote($('#plate .vote-btn-yes'), 'YEAH');
            app.submitVote($('#plate .vote-btn-yes'), 'nay');
            expect(jasmine.Ajax.requests.count()).toBe(0);
            expect(localStorage.getItem('has_voted_1')).toBeFalsy();
        });
    });
    
    describe('submitReply', function() {
        beforeEach(function() {
            app.insertPages();
            app.loadReflection($('#mirror'), fakeReflectionData);
            localStorage.setItem('token', 'qwertyuiop');
            localStorage.setItem('last_retrieve', 'never');
            this.form = $('#mirror .reflection-response');
            this.form.find('[name="p"]').val('tester');
            this.form.find('[name="r"]').val('this is a test response');
            app.submitReply(this.form);
            spyOn(app, 'appendReply');
        });
        it('submits reflection replies to the server', function() {
            expect(this.form).toBeHidden();
            var requests = jasmine.Ajax.requests;
            expect(requests.count()).toBe(1);
            var post = requests.at(0);
            expect(post.method).toBe('POST');
            expect(post.url).toBe('/reflection/2/reply');
            expect(post.requestHeaders['X-Requested-With'])
                .toBe('XMLHttpRequest');
            expect(post.requestHeaders['Content-Type'])
                .toBe('application/x-www-form-urlencoded; charset=UTF-8');
            expect(post.params)
                .toBe('p=tester&r=this+is+a+test+response&t=qwertyuiop&last-retrieve=never&ca=');
        });
        it('appends the reply and resets the form on success', function() {
            var post = jasmine.Ajax.requests.at(0);
            post.respondWith({
                'status': 200,
                'contentType': 'application/json',
                'responseText': JSON.stringify({
                    'status': 'success',
                    'token': '1234567890'
                })
            });
            expect(localStorage.getItem('token')).toBe('1234567890');
            expect(app.appendReply).toHaveBeenCalledWith($('#mirror'), {
                pseudonym: 'tester',
                message: 'this is a test response'
            });
            expect(this.form.find('[name="r"]')).toHaveValue('');
            expect(this.form).toBeVisible();
        });
        it('updates the thread and offers a retry in case of ninjas', function() {
            var post = jasmine.Ajax.requests.at(0);
            $('<p>').addClass('reply-submitted').appendTo('#mirror');
            post.respondWith({
                'status': 200,
                'contentType': 'application/json',
                'responseText': JSON.stringify({
                    'status': 'ninja',
                    'token': '1234567890',
                    'since': 'now',
                    'new': [{}, {}]
                })
            });
            expect(localStorage.getItem('token')).toBe('1234567890');
            expect(localStorage.getItem('last_retrieve')).toBe('now');
            expect($('#mirror .reply-submitted')).not.toBeInDOM();
            expect(app.appendReply.calls.count()).toBe(2);
            expect(this.form.find('[name="r"]'))
                .toHaveValue('this is a test response');
            expect(this.form).toBeVisible();
            expect($('#mirror .ninja-message')).toBeVisible();
        });
        it('presents a captcha challenge on server request', function() {
            var post = jasmine.Ajax.requests.at(0);
            post.respondWith({
                'status': 200,
                'contentType': 'application/json',
                'responseText': JSON.stringify({
                    'status': 'captcha',
                    'token': '1234567890',
                    'captcha_challenge': 'banana banana banana'
                })
            });
            expect(localStorage.getItem('token')).toBe('1234567890');
            expect(app.appendReply).not.toHaveBeenCalled();
            expect(this.form.find('[name="r"]'))
                .toHaveValue('this is a test response');
            expect(this.form).toBeHidden();
            expect($('#mirror .captcha-popup')).toBeVisible();
            expect($('#mirror .captcha-challenge'))
                .toHaveText('banana banana banana');
        });
        it('notifies the user if the thread has been closed', function() {
            var post = jasmine.Ajax.requests.at(0);
            var announcement = $('#mirror .reflection-closure-announce');
            announcement.show();
            post.respondWith({
                'status': 400,
                'contentType': 'application/json',
                'responseText': JSON.stringify({
                    'status': 'closed',
                    'token': '1234567890'
                })
            });
            expect(localStorage.getItem('token')).toBe('1234567890');
            expect(app.appendReply).not.toHaveBeenCalled();
            expect(this.form).toBeHidden();
            expect(announcement).toBeHidden();
            expect($('#mirror .reflection-closed-popup')).toBeVisible();
            expect($('#mirror .reflection-closed-notice')).toBeVisible();
        });
        it('offers a retry if the submitted form was invalid', function() {
            var post = jasmine.Ajax.requests.at(0);
            post.respondWith({
                'status': 400,
                'contentType': 'application/json',
                'responseText': JSON.stringify({
                    'status': 'invalid',
                    'token': '1234567890'
                })
            });
            expect(localStorage.getItem('token')).toBe('1234567890');
            expect(app.appendReply).not.toHaveBeenCalled();
            expect(this.form).toBeVisible();
            expect($('#mirror .reflection-invalid-popup')).toBeVisible();
        });
    });
    
    describe('submitCaptcha', function() {
        beforeEach(function() {
            app.insertPages();
            app.loadReflection($('#mirror'), fakeReflectionData);
            localStorage.setItem('token', 'qwertyuiop');
            localStorage.setItem('last_retrieve', 'never');
            this.form = $('#mirror .reflection-response');
            this.form.find('[name="p"]').val('tester');
            this.form.find('[name="r"]').val('this is a test response');
            $('#mirror .captcha-popup').popup('open', {positionTo: 'window'});
            spyOn(app, 'submitReply').and.callThrough();
        });
        it('defers to submitReply to send the captcha response', function() {
            var captcha = $('#mirror .reflection-captcha');
            var response = captcha.find('[name="ca"]');
            response.val('banana banana banana');
            app.submitCaptcha(captcha);
            expect($('#mirror .captcha-popup').parent())
                .toHaveClass('ui-popup-hidden');
            expect(response).toHaveValue('');
            expect(app.submitReply).toHaveBeenCalledWith(this.form);
            var requests = jasmine.Ajax.requests;
            expect(requests.count()).toBe(1);
            var post = requests.at(0);
            expect(post.method).toBe('POST');
            expect(post.url).toBe('/reflection/2/reply');
            expect(post.requestHeaders['X-Requested-With'])
                .toBe('XMLHttpRequest');
            expect(post.requestHeaders['Content-Type'])
                .toBe('application/x-www-form-urlencoded; charset=UTF-8');
            expect(post.params)
                .toBe('p=tester&r=this+is+a+test+response&t=qwertyuiop&last-retrieve=never&ca=banana+banana+banana');
        });
    });
    
    describe('appendReply', function() {
        beforeEach(function() {
            app.insertPages();
            this.responses = fakeReflectionData.responses;
            spyOn(app, 'submitReplyVote');
        });
        it('appends moderatable reflection replies to the thread', function() {
            _(this.responses).each(function(r) {
                app.appendReply($('#mirror'), r);
            });
            expect($('.reply-1')).toBeInDOM();
            expect($('.reply-1')).toContainHtml('<span class="reply-date">2015-03-02</span><span class="reply-nick">malbolge</span><span class="reply-content">&lt;script&gt;wreakHavoc();&lt;/script&gt;</span><br><a href="#" class="reply-vote ui-btn ui-icon-plus ui-btn-icon-left">leerzaam</a><a href="#" class="reply-vote ui-btn ui-icon-minus ui-btn-icon-right">ongewenst</a>');
            expect($('.reply-1 > h3')).toBeInDOM();
            expect($('.reply-1 > h3')).toContainHtml('<span class="reply-date">2015-03-02</span> <span class="reply-nick">spam</span>');
            expect($('.reply-2')).toBeInDOM();
            expect($('.reply-2')).toHaveHtml('<h3 class="reply-synopsis" style="display: none;"><span class="reply-date">2015-03-03</span> <span class="reply-nick">victim</span></h3><span class="reply-date">2015-03-03</span><span class="reply-nick">victim</span><span class="reply-content">help me</span><br><a href="#" class="reply-vote ui-btn ui-icon-plus ui-btn-icon-left">leerzaam</a><a href="#" class="reply-vote ui-btn ui-icon-minus ui-btn-icon-right">ongewenst</a>');
            $('.reply-1 .reply-vote.ui-icon-minus').click();
            expect(app.submitReplyVote).toHaveBeenCalledWith(1, 'down');
            $('.reply-2 .reply-vote.ui-icon-plus').click();
            expect(app.submitReplyVote).toHaveBeenCalledWith(2, 'up');
        });
    });

    describe('submitReplyVote', function() {
        beforeEach(function() {
            app.insertPages();
            app.loadReflection($('#mirror'), fakeReflectionData);
            localStorage.setItem('token', 'qwertyuiop');
        });
        it('communicates thread moderation votes with the server', function() {
            app.submitReplyVote(2, 'up');
            var requests = jasmine.Ajax.requests;
            expect(requests.count()).toBe(1);
            var post = requests.at(0);
            expect(post.method).toBe('POST');
            expect(post.url).toBe('/reply/2/moderate/');
            expect(post.requestHeaders['X-Requested-With'])
                .toBe('XMLHttpRequest');
            expect(post.requestHeaders['Content-Type'])
                .toBe('application/x-www-form-urlencoded; charset=UTF-8');
            expect(post.params).toBe('choice=up&t=qwertyuiop');
            post.respondWith({
                'status': 200,
                'contentType': 'application/json',
                'responseText': JSON.stringify({
                    'status': 'success',
                    'token': '1234567890'
                })
            });
            expect(localStorage.getItem('token')).toBe('1234567890');
            expect($('.reply-2 .reply-vote')).toBeHidden();
            expect($('<div>').append($('.reply-2 > *:last'))).toHaveHtml(
                '<em style="color: green;">Bedankt voor je stem!</em>'
            );
        });
        it('rejects any vote value other than "up" or "down"', function() {
            app.submitReplyVote(2, 'more');
            app.submitReplyVote(2, 'less');
            app.submitReplyVote(2, 'yes');
            app.submitReplyVote(2, 'no');
            app.submitReplyVote(2, 'UP');
            app.submitReplyVote(2, 'DOWN');
            expect(jasmine.Ajax.requests.count()).toBe(0);
        });
    });

    describe('getScore', function() {
        it('calculates a score in the range [0, 1],', function() {
            var test = app.getScore(0, 0);
            expect(test).not.toBeGreaterThan(1);
            expect(test).not.toBeLessThan(0);
            test = app.getScore(0, 1e9);
            expect(test).not.toBeGreaterThan(1);
            expect(test).not.toBeLessThan(0);
            test = app.getScore(1e9, 0);
            expect(test).not.toBeGreaterThan(1);
            expect(test).not.toBeLessThan(0);
            test = app.getScore(1e9, 1e9);
            expect(test).not.toBeGreaterThan(1);
            expect(test).not.toBeLessThan(0);
        });
        it('where more upvotes begets a greater score,', function() {
            var test1 = app.getScore( 0, 10);
            var test2 = app.getScore( 5, 10);
            var test3 = app.getScore(10, 10);
            var test4 = app.getScore(15, 10);
            expect(test1).toBeLessThan(test2);
            expect(test2).toBeLessThan(test3);
            expect(test3).toBeLessThan(test4);
        });
        it('where more downvotes begets a lesser score,', function() {
            var test1 = app.getScore(10,  0);
            var test2 = app.getScore(10,  5);
            var test3 = app.getScore(10, 10);
            var test4 = app.getScore(10, 15);
            expect(test1).toBeGreaterThan(test2);
            expect(test2).toBeGreaterThan(test3);
            expect(test3).toBeGreaterThan(test4);
        });
        it('where the benefit of the doubt is given in the face of uncertainty,', function() {
            var test1 = app.getScore(   1,    1);
            var test2 = app.getScore(  10,   10);
            var test3 = app.getScore( 100,  100);
            var test4 = app.getScore(1000, 1000);
            expect(test1).toBeGreaterThan(test2);
            expect(test2).toBeGreaterThan(test3);
            expect(test3).toBeGreaterThan(test4);
        });
        it('and where the score approaches the upvote proportion with increasing certainty', function() {
            expect(app.getScore(1e9, 9e9)).toBeCloseTo(.1, 3);
            expect(app.getScore(3e9, 7e9)).toBeCloseTo(.3, 3);
            expect(app.getScore(5e9, 5e9)).toBeCloseTo(.5, 3);
            expect(app.getScore(7e9, 3e9)).toBeCloseTo(.7, 3);
            expect(app.getScore(9e9, 1e9)).toBeCloseTo(.9, 3);
        });
    });

    xdescribe('displayVotes', function() {
        
    });

    xdescribe('displayVoteButtons', function() {
        
    });

    xdescribe('bindEvents', function() {
        
    });

    describe('onDeviceReady', function() {
        it('should report that it fired', function() {
            spyOn(app, 'receivedEvent');
            app.onDeviceReady();
            expect(app.receivedEvent).toHaveBeenCalledWith('deviceready');
        });
    });

    describe('receivedEvent', function() {
    });
});
