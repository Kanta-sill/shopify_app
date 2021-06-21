from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


class ShopifyDiscountPreview(models.Model):
    _name = "shopify.discount.preview"
    _description = "Preview"
    _rec_name = 'shop'

    shop = fields.Many2one('shopify.shop', string='Shop ID', readonly=True)
    discount_color = fields.Char(string='Discount Color', default='#000000', store=True)
    discount_sample = fields.Html(string='Discount sample', compute="_compute_discount_sample")
    amount_color = fields.Char(string='Amount Color', default='#000000', store=True)
    amount_sample = fields.Html(string='Discount sample', compute="_compute_amount_sample")
    voucho_color = fields.Char(string='Voucho Color', default='#000000', store=True)
    voucho_sample = fields.Html(string='Discount sample', compute="_compute_voucho_sample")

    @api.onchange('discount_color')
    def _compute_discount_sample(self):
        for rec in self:
            rec.sudo().discount_sample = None
            if rec.sudo().discount_color:
                rec.sudo().discount_sample = '<p style="color: ' + str(rec.sudo().discount_color) + ';">Discount</p>'

    @api.onchange('amount_color')
    def _compute_amount_sample(self):
        for rec in self:
            rec.sudo().amount_sample = None
            if rec.sudo().amount_color:
                rec.sudo().amount_sample = '<p style="color: ' + str(rec.sudo().amount_color) + ';">1.000.000 VND</p>'

    @api.onchange('voucho_color')
    def _compute_voucho_sample(self):
        for rec in self:
            rec.sudo().voucho_sample = None
            if rec.sudo().voucho_color:
                rec.sudo().voucho_sample = '<p style="color: ' + str(
                    rec.sudo().voucho_color) + ';">Voucho: -100.000 VND</p>'

    @api.model
    def create(self, vals):
        flag = False
        shop_preview = self.sudo().env['shopify.discount.preview'].search([])
        for pre in shop_preview:
            if pre.shop.id == vals['shop']:
                flag = True
                break
        if not vals['shop']:
            raise UserError(_("You must choose shop"))
        if flag:
            raise UserError(_("One shop can create only one preview"))
        else:
            result = super(ShopifyDiscountPreview, self).create(vals)
            return result
