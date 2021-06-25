from odoo import api, fields, models, _, tools


class ShopifyDiscountChooseProduct(models.TransientModel):
    _name = "shopify.discount.choose.product"
    _description = "Choose Product"

    discount_id = fields.Many2one('shopify.discount.program', string='Discount', readonly=True)

    pro_ids = fields.One2many('shopify.discount.choose.product.get.product', 'discount_id',
                              string='Discount Product ID')

    def choose_discount_product(self):
        discount_product = self.env['shopify.discount.program.product'].sudo().search(
            [('discount_id', '=', self.discount_id.id)])
        pro_id_list = []
        for pro in discount_product:
            pro_id_list.append(pro.pro_id)
        pro_list = self.env['shopify.discount.choose.product.get.product'].sudo().search(
            [('discount_id', '=', self.id), ('check_product', '=', True)])
        pro_id_lists = []
        for pro in pro_list:
            pro_id_lists.append(pro.pro_id)
        for discount in discount_product:
            if discount.pro_id not in pro_id_lists:
                discount.unlink()

        for pro in pro_list:
            if pro.pro_id not in pro_id_list:
                pro_vals = {
                    'discount_id': self.discount_id.id,
                    'pro_id': pro.pro_id,
                    'name': pro.name
                }
                self.env['shopify.discount.program.product'].sudo().create(pro_vals)
        pass


class ShopifyDiscountProduct(models.TransientModel):
    _name = "shopify.discount.choose.product.get.product"

    discount_id = fields.Many2one('shopify.discount.choose.product', string='Discount ID')
    pro_id = fields.Char(string='Pro ID')
    name = fields.Char(string='Name')
    check_product = fields.Boolean(string='Choose')
