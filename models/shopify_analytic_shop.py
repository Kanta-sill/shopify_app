from odoo import api, fields, models, _, tools
import datetime

class ShopifyAnalytic(models.Model):
    _name = "shopify.analytic.shop"
    _description = "Shop Analytic"

    shop_id = fields.Many2one('shopify.shop', string='Shop ID')
    discount_name = fields.Char(string='Discount Name')
    product_info = fields.Char(string='Product')
    create_month = fields.Char(string='Create Month', compute='get_create_month', store=True)

    def get_create_month(self):
        current = datetime.datetime.now()
        month_current = current.strftime("%m/%Y")
        self.create_month = month_current