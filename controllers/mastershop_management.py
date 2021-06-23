import json

from odoo import http
from odoo.http import request

import shopify
import datetime


class MasterShopReport(http.Controller):
    @http.route('/report/mastershop_report_dashboard', type='http', auth='public')
    def mastershop_analytic_graph_bar(self, **kwargs):
        return request.render('shopify_app.mastershop_report_dashboard_iframe_template')

    def item_sort(self, item_list, item_name):
        def sort_item_value(item):
            return item['Quantity']

        item_info = []
        while item_list:
            item_quantity = item_list.count(item_list[0])
            item = item_list[0]
            for i in range(item_quantity):
                item_list.remove(item)
            item_info.append({item_name: item, 'Quantity': item_quantity})
        item_info.sort(reverse=True, key=sort_item_value)
        return item_info[:10]

    @http.route('/shopify_data/analytic_bar/<string:shop>', auth='public', type='json', cors='*', csrf=False)
    def odoo_fetch_checkout(self, shop, *kwargs):
        shop_app_id = request.env['shopify.shop.app'].sudo().search([('shop', '=', shop)])
        app_id = request.env['shopify.app'].sudo().search([('id', '=', shop_app_id.app.id)])
        API_KEY = app_id.api_key
        API_SECRET = app_id.secret_key
        api_version = app_id.api_version
        TOKEN = shop_app_id.token

        shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)
        shopify_session = shopify.Session(shop, api_version, token=TOKEN)
        shopify.ShopifyResource.activate_session(shopify_session)

        # Get current time
        current = datetime.datetime.now()
        month_current = current.strftime("%m/%Y")
        pro_list = []
        discount_list = []
        shop_order = shopify.Order.find(financial_status='paid')
        for order in shop_order:
            order_create = order.created_at
            order_date = ''.join(order_create.rsplit(':', 1))
            month_date = datetime.datetime.strptime(order_date, '%Y-%m-%dT%H:%M:%S%z')
            if month_date.strftime("%m/%Y") == month_current:

                # Get list of products
                for item in order.line_items:
                    for i in range(item.quantity):
                        pro_list.append(item.name)

                # Get list of discounts
                meta_id = order.note_attributes[0].value
                meta = shopify.Metafield.find(id=meta_id)
                meta_parse = json.loads(meta[0].value)
                for discount in meta_parse:
                    discount_list.append(discount['discount_program'])

        product_quan = self.item_sort(pro_list, 'Product')
        discount_quan = self.item_sort(discount_list, 'Discount')

        products = []
        product_quantity = []
        discounts = []
        discount_quantity = []

        # Take products for name and quantity
        for var in product_quan:
            products.append(var['Product'])
            product_quantity.append(var['Quantity'])

        # Take discounts for name and quantity
        for var in discount_quan:
            discounts.append(var['Discount'])
            discount_quantity.append(var['Quantity'])

        return {
            'month': month_current,
            'products': products,
            'product_quantity': product_quantity,
            'discounts': discounts,
            'discount_quantity': discount_quantity
        }
