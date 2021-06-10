from odoo import api, fields, models, _, tools


class ShopifyDiscountChooseProduct(models.TransientModel):
    _name = "shopify.discount.choose.product"
    _description = "Choose Product"

    discount_id = fields.Many2one('shopify.discount.program', string='Discount', readonly=True)

    pro_ids = fields.One2many('shopify.discount.choose.product.get.product', 'discount_id',
                              string='Discount Product ID')

    def choose_discount_product(self):
        discount_product = self.env['shopify.discount.program.product'].search(
            [('discount_id', '=', self.discount_id.id)])
        pro_id_list = []
        for pro in discount_product:
            pro_id_list.append(pro.product_id.id)
        pro_list = self.env['shopify.discount.choose.product.get.product'].search(
            [('discount_id', '=', self.id), ('check_product', '=', True)])

        for pro in pro_list:
            if pro.product_id.id not in pro_id_list:
                pro_vals = {
                    'discount_id': self.discount_id.id,
                    'product_id': pro.product_id.id
                }
                self.env['shopify.discount.program.product'].create(pro_vals)
        pass


class ShopifyDiscountProduct(models.TransientModel):
    _name = "shopify.discount.choose.product.get.product"

    discount_id = fields.Many2one('shopify.discount.choose.product', string='Discount ID')
    product_id = fields.Many2one('shopify.product.load', string='Product ID')
    price = fields.Float(related='product_id.price')
    check_product = fields.Boolean(string='Choose')
