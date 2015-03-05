/*
    (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
    Author: Julian Gonggrijp, j.gonggrijp@uu.nl
*/
describe('app', function() {
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
        function fakeJQueryGet (url, data, success, dataType) {
            if (url === '/case/') success({
                'id': 1,
                'title': 'testcasus',
                'publication': '2015-03-02',
                'week': '10',
                'closure': null,
                'text': 'some dummy text',
                'proposition': 'difficult question',
                'picture': null,
                'background': '#998877'
            }, '200 OK');
        };
        beforeEach(function() {
            $('#stage').html('<div id="plate">' +
                '<h3>Casus van week <span class="week-number"></span></h3>' +
                '<div id="case-display" style="width: 18em; height: 12em; background: #808080"></div>' +
                '<p id="case-text"></p>' +
                '<p id="case-proposition"></p>' +
                '<a href="#" class="ui-btn ui-btn-inline ui-corner-all">Ja</a>' +
                '<a href="#" class="ui-btn ui-btn-inline ui-corner-all">Nee</a>' +
                '</div>');
            spyOn($, 'get').and.callFake(fakeJQueryGet);
        });
        it('must prepopulate the HTML content with casus data', function() {
            app.preloadContent();
            expect($('#plate .week-number').html()).toBe('10');
            expect($('#case-text').html()).toBe('some dummy text');
            expect($('#case-proposition').html()).toBe('difficult question');
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
