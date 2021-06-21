const base_url = 'https://odoo.website'

odoo.define('shopify_app.mastershop_report_analytic_js', function (require) {
    'use strict'
    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var FormRenderer = require('web.FormRenderer');
    var viewRegistry = require('web.view_registry');

    function mastershop_analytic_graph_bar(data) {
        var shop = data.shop_id.data['display_name']
        $.ajax({
            type: 'POST',
            url: base_url + '/shopify_data/analytic_bar/' + shop,
            dataType: 'json',
            data: JSON.stringify({jsonrpc: '2.0'}),
            contentType: 'application/json',
            error: function (request, error) {
                console.log('error')
            },
            complete: function (data) {
                var productDetail = JSON.parse(data['responseText'])['result']
                var ListProductValue = ''
                for (var i=0; i<productDetail['products'].length; i++) {
                    ListProductValue += '\'' + productDetail['products'][i] + '\','
                }
                var ListProductQuantity = productDetail['product_quantity'].toString()

                var ListDiscountValue = ''
                for (var i=0; i<productDetail['discounts'].length; i++) {
                    ListDiscountValue += '\'' + productDetail['discounts'][i] + '\','
                }
                var ListDiscountQuantity = productDetail['discount_quantity'].toString()

                var month = productDetail['month']
                var analyticGraphBar = '<script>\n' +
                    '\tif((typeof myChartBar) == \'object\') {\n' +
                    '\t}else {\n' +
                    '  \t  var ctxbar = document.getElementById(\'discount_graph_bar_id\').getContext(\'2d\');\n' +
                    '          var myChartBar = new Chart(ctxbar, {\n' +
                    '            type: \'bar\',\n' +
                    '            data: {\n' +
                    '\t\tlabels: [' + ListDiscountValue + '],\n' +
                    '                datasets: [{\n' +
                    '                    label: \'Top Discount ' + month + '\',\n' +
                    '                    data: [' + ListDiscountQuantity + '],\n' +
                    '                    fill: false,\n' +
                    '                    borderColor: \'green\',\n' +
                    '                    backgroundColor: \'#A1F7BB\',\n' +
                    '                },]\n' +
                    '            },\n' +
                    '        });\n' +
                    '  \t  var ctxProduct = document.getElementById(\'product_graph_bar_id\').getContext(\'2d\');\n' +
                    '          var productChartBar = new Chart(ctxProduct, {\n' +
                    '            type: \'bar\',\n' +
                    '            data: {\n' +
                    '\t\tlabels: [' + ListProductValue + '],\n' +
                    '                datasets: [{\n' +
                    '                    label: \'Top Product ' + month + '\',\n' +
                    '                    data: [' + ListProductQuantity + '],\n' +
                    '                    fill: false,\n' +
                    '                    borderColor: \'green\',\n' +
                    '                    backgroundColor: \'#eda634\',\n' +
                    '                },]\n' +
                    '            },\n' +
                    '        });\n' +
                    '\t}\n' +
                    '</script>'
                $('#mastershop_report_dashboard_iframe').contents().find('#mastershop_analytic_graph_bar').after(analyticGraphBar)
            }
        })
    }

    function re_draw_shopify_mastershop_analytic_graph_bar(data) {
        let first_time_draw_graph_bar_iframe_interval;
        first_time_draw_graph_bar_iframe_interval = setInterval(function () {
            var iframeGraphBar = document.getElementById('mastershop_report_dashboard_iframe');
            if (iframeGraphBar != undefined) {
                var iframeDocGraphBar = iframeGraphBar.contentDocument || iframeGraphBar.contentWindow.document;
                if (iframeDocGraphBar.readyState == 'complete') {
                    if ($("#mastershop_report_dashboard_iframe").contents().find("#mastershop_analytic_graph_bar") != undefined &&
                        $("#mastershop_report_dashboard_iframe").contents().find("#mastershop_analytic_graph_bar").length > 0) {
                        clearInterval(first_time_draw_graph_bar_iframe_interval);
                        mastershop_analytic_graph_bar(data)
                        // var ctx = document.getElementById("chart_graph_line_id")
                    }
                }
            }
        }, 100)
    }

    var OurFormController = FormController.extend({
        customer_events: _.extend({}, FormController.prototype.customer_events, {
            Controller: FormController,
            Renderer: FormRenderer,
            jsLibs: [
                '/web/static/lib/Chart/Chart.js',
            ],
        }),
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments)
        },
        _confirmChange: function (id, fields, e) {
            re_draw_shopify_mastershop_analytic_graph_bar(this.model.get(e.target.dataPointID).data)
            return this._super.apply(this, arguments)
        },
        _update: function (state, params) {
            var result = this._super.apply(this, arguments)
            re_draw_shopify_mastershop_analytic_graph_bar(state.data)
            return result;
        },
    })

    var OurFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: OurFormController,
            Renderer: FormRenderer
        })
    })
    viewRegistry.add('mastershop_report_analytic', OurFormView)
    return OurFormView
})