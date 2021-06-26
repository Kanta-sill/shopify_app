odoo.define('shopify_app.quick_publish', function (require) {
    'use strict';

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var _t = core._t;

    var MastershopAnalyticDataGraphBar = AbstractField.extend({
        template: 'MastershopWebsitePublish',
        events: {},
        start: function () {
            return this._super.apply(this, arguments);
        },
        isSet: function () {
            return true;
        },
        _render: function () {
            var self = this;
            if (this.recordData.shop_id) {
                var analyticGraphBars = '<script>\n' +
                    '    var result = [' + this.recordData.data_analytic + ']\n' +
                    '    function myShow(a, myCallBack) {\n' +
                    '        myCallBack(a)\n' +
                    '    }\n' +
                    '    myShow(result, get_test_graph_bar)\n' +
                    '</script>'
                setTimeout(function () {
                    self.$el.after(analyticGraphBars)
                }, 10);
            }
            // return this._super.apply(this, arguments);
        },
    });
    var OurFormController = FormController.extend({
        customer_events: _.extend({}, FormController.prototype.customer_events, {
            jsLibs: [
                '/web/static/lib/Chart/Chart.js',
            ],
        }),
    })
    var OurFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: OurFormController,
        })
    })
    viewRegistry.add('mastershop_report_analytic', OurFormView)

    field_registry.add('graph_bar_analytic', MastershopAnalyticDataGraphBar)
});