require.config({
    baseUrl: '/static/libraries',
    paths: {
        'domReady': 'domReady/domReady',
        'text': 'text/text',
        'i18n': 'i18n/i18n',
        'jquery': 'jquery/dist/jquery.min',
        'underscore': 'underscore/underscore-min',
        'string': 'string/lib/string.min',
        'backbone': 'backbone/backbone',
        'hammerjs': 'hammerjs/hammer.min',
        'jquery-hammerjs': 'jquery-hammerjs/jquery.hammer',
        'backbone.validation': 'backbone-validation/dist/backbone-validation-amd-min',
        'backbone.localstorage': 'backbone-localStorage/backbone.localStorage-min',
        'backbone.hammerjs': 'backbone.hammer/backbone.hammer',
        'backbone.wreqr' : 'hbackbone.wreqr/lib/backbone.wreqr.min',
        'backbone.babysitter': 'backbone.babysitter/lib/backbone.babysitter.min',
        'backbone.marionette' : 'backbone.marionette/lib/core/backbone.marionette.min',
        'uikit': 'uikit/js/uikit.min',
        'moment': 'moment/min/moment.min',
        'Chart': 'chartjs/Chart.min',
        'models': '../models',
        'views': '../views',
        'controllers': '../controllers',
        'collections': '../collections',
        'templates': '../templates'
    },

    config: {
        "uikit": {
            "base": '../libraries/uikit/js'
        }
    }
});
