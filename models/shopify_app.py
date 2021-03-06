from odoo import api, fields, models, _, tools


class ShopifyApp(models.Model):
    _name = "shopify.app"
    _description = "Shopify App"
    _rec_name = 'app_name'

    api_key = fields.Char(string='API Key')
    secret_key = fields.Char(string='Secret Key')
    api_version = fields.Char(string='API Version')
    app_name = fields.Char(string='App Name')
    base_url = fields.Char(string='Base URL')

