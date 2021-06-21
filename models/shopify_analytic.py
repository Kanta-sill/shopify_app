from odoo import api, fields, models, _, tools


class ShopifyAnalytic(models.Model):
    _name = "shopify.analytic"
    _description = "Shopify App"

    shop_id = fields.Many2one('shopify.shop', string='Shop ID')
    name = fields.Char(string='Name')
