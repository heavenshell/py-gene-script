define([
  'jquery',
  'underscore',
  'backbone',
  'log',
  'views/AppView'
], function ($, _, Backbone, log, AppView) {
  var AppRouter = Backbone.Router.extend({
    routes: {
      '':        'root',
      '__debug': 'debug'
    }
  });
  var initialize = function(){
    var router = new AppRouter();
    router.on('route:root', function () {
      log.setLevel('info');
      var app = new AppView();
      app.render();
    });
    router.on('route:debug', function () {
      log.setLevel('debug');
      log.debug('Debug mode start');
      var app = new AppView();
      app.render();
    });

    Backbone.history.start();
  };

  return {
    initialize: initialize
  };
});

