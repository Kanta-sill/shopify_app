from odoo import api, fields, models, _, tools


class ShopifyShopApp(models.Model):
    _name = "shopify.shop.app"
    _description = "Shopify App"

    shop = fields.Many2one('shopify.shop', string='Shop')
    app = fields.Many2one('shopify.app', string='App')
    token = fields.Char(string='Token')