from odoo import api, fields, models, _, tools


class ShopifyContactInherit(models.Model):
    _inherit = 'res.partner'

    shop_id = fields.Many2one('shopify.shop', string='Shop ID')
