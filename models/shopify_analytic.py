from odoo import api, fields, models, _, tools


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
