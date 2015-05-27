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
    
    function fakeJQueryGet (url, data, success, dataType) {
        return {
            query: url,
            done: function(callback) {
                if (this.query === '/case/') callback(fakeLatestCaseData);
            }
        };
    };
    
    describe('initialize', function() {
        var emulateDeviceReady = function(callback) {
            app.initialize();
            helper.trigger(window.document, 'deviceready');
            callback();
        };
        beforeEach(function(done) {
            spyOn(app, 'onDeviceReady');
            spyOn(app, 'preloadContent');
            emulateDeviceReady(done);
        });
        it('should bind deviceready', function() {
            expect(app.onDeviceReady).toHaveBeenCalled();
        });
        it('should preload content', function() {
            expect(app.preloadContent).toHaveBeenCalled();
        });
    });
    
    describe('preloadContent', function() {
        beforeEach(function() {
            app.insertPages();
            $('#stage').empty();
            $('#plate, #plate-archive-item, #mirror, #mirror-archive-item')
                .appendTo('#stage');
            spyOn($, 'get').and.callFake(fakeJQueryGet);
        });
        it('must prepopulate the HTML content with casus data', function() {
            app.loadCasus($('#plate'), fakeLatestCaseData);
            expect($('#plate .week-number').html()).toBe('10');
            expect($('#plate .case-text').html()).toBe('some dummy text');
            expect($('#plate .case-proposition').html()).toBe('difficult question');
        });
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
