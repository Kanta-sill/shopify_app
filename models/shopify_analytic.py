from odoo import api, fields, models, _, tools

import datetime
import json


class ShopifyAnalytic(models.Model):
    _name = "shopify.analytic"
    _description = "Shopify App"

    def get_discount_shop(self):
        user_current = self.env['res.users'].sudo().search([('id', '=', self._uid)])
        shop_current = self.env['shopify.shop'].sudo().search([('base_url', '=', user_current.login)])
        if shop_current:
            return shop_current.id
        else:
            return None

    shop_id = fields.Many2one('shopify.shop', string='Shop ID', default=get_discount_shop)
    name = fields.Char(string='Name')
    data_analytic = fields.Char(string='Data', compute='get_data_analytic')

    def get_data_analytic(self):
        self.data_analytic = ''

        current = datetime.datetime.now()
        month_current = current.strftime("%m/%Y")
        analytic_info = self.env['shopify.analytic.shop'].search(
            [('create_month', '=', month_current), ('shop_id', '=', self.shop_id.id)])
        discount_name_list = ''
        product_name_list = ''
        for discount in analytic_info:
            discount_name_list += discount.discount_name
            product_name_list += discount.product_info

        products = []
        product_quantity = []
        discounts = []
        discount_quantity = []
        product_quan = self.item_sort(product_name_list.split(',')[:-1], 'Product')
        discount_quan = self.item_sort(discount_name_list.split(',')[:-1], 'Discount')

        # Take products for name and quantity
        for var in product_quan:
            products.append(var['Product'])
            product_quantity.append(var['Quantity'])

        # Take discounts for name and quantity
        for var in discount_quan:
            discounts.append(var['Discount'])
            discount_quantity.append(var['Quantity'])

        data_final = json.dumps({
            'month': month_current,
            'products': products,
            'product_quantity': product_quantity,
            'discounts': discounts,
            'discount_quantity': discount_quantity
        })
        self.data_analytic = data_final

    # Sort the item by quantity
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
