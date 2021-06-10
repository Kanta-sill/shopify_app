from odoo import api, fields, models, _, tools


class ShopifyProductLoad(models.Model):
    _name = "shopify.product.load"
    _description = "Shop Product"

    name = fields.Char(string='Name')
    product_id = fields.Char(string='Product ID')
    variant_id = fields.Char(string='Variant ID')
    price = fields.Float(string='Price')
    shop_id = fields.Many2one(string='Shop ID')

    discount_id = fields.One2many('shopify.discount.program.product', 'product_id', string='Discount Program')
