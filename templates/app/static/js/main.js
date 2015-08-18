'use strict'
require.config({
  shim: {
    'jquery': {
      exports: '$'
    },
    'bootstrap': {
      deps: ['jquery']
    },
    'underscore': {
      exports: '_'
    },
    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    },
    'log': {
      exports: 'log'
    }
  },
  paths: {
    'jquery':     'libs/jquery-1.10.1-min',
    'bootstrap':  'libs/bootstrap-2.3.2-min',
    'underscore': 'libs/underscore-1.4.3-min',
    'backbone':   'libs/backbone-1.0.0-min',
    'text':       'libs/text-2.0.7',
    'log':        'libs/micro-log-0.0.1'
  },
  urlArgs: 'bust=' +  (new Date()).getTime()
});

require([
  'router',
  'jquery',
  'bootstrap',
  'log'
], function (App) {
  App.initialize();
});

