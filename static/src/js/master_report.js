odoo.define('shopify_app.quick_publish', function (require) {
    'use strict';

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var _t = core._t;

    var QickWebsitePublishButton = AbstractField.extend({
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
            var shop = this.recordData.shop_id.data.display_name;
            this._rpc({
                model: this.model,
                method: 'quick_publish_products',
                args: [this.res_id],
                kwargs: {
                    shop: shop,
                }
            }).then(function (result) {
                var month = result['month'].split('/')

                var ListProductValue = ''
                for (var i = 0; i < result['products'].length; i++) {
                    ListProductValue += '\'' + result['products'][i] + '\','
                }
                var ListProductQuantity = result['product_quantity'].toString()

                var ListDiscountValue = ''
                for (var i = 0; i < result['discounts'].length; i++) {
                    ListDiscountValue += '\'' + result['discounts'][i] + '\','
                }
                var ListDiscountQuantity = result['discount_quantity'].toString()

                var analyticGraphBars = '<script>\n' +
                    '    var productValues = [' + ListProductValue + ']\n' +
                    '    var productQuantitys = [' + ListProductQuantity + ']\n' +
                    '    var discountValues = [' + ListDiscountValue + ']\n' +
                    '    var discountQuantitys = [' + ListDiscountQuantity + ']\n' +
                    '    var month_current = [' + month + ']\n' +
                    '    function myShow(a, b, c, d, e, myCallBack) {\n' +
                    '        myCallBack(a, b, c, d, e)\n' +
                    '    }\n' +
                    '    myShow(productValues, productQuantitys, discountValues, discountQuantitys, month_current, get_test_graph_bar)\n' +
                    '</script>'
                self.$el.after(analyticGraphBars)
            });
            // return this._super.apply(this, arguments);
        },
    });
    field_registry.add('quick_publish_button', QickWebsitePublishButton)
});