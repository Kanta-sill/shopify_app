import werkzeug

from odoo import api, fields, models, _, tools
import shopify


class ShopifyDiscountProgram(models.Model):
    _name = "shopify.discount.program"
    _description = "Discount Program"

    def get_discount_shop(self):
        user_current = self.env['res.users'].search([('id', '=', self._uid)])
        shop_current = self.env['shopify.shop'].search([('base_url', '=', user_current.login)])
        if shop_current:
            return shop_current.id
        else:
            return None

    name = fields.Char(string='Name')
    shop_id = fields.Many2one('shopify.shop', string='Shop ID', default=get_discount_shop)

    cus_ids = fields.One2many('shopify.discount.program.customer', 'discount_id', string='Discount Customer ID')
    pro_ids = fields.One2many('shopify.discount.program.product', 'discount_id', string='Discount Product ID')

    @api.depends('shop_id')
    def update_shopify_product(self):
        if self.shop_id:
            shop_app_id = self.env['shopify.shop.app'].sudo().search([('shop', '=', self.shop_id.id)])
            app_id = self.env['shopify.app'].sudo().search([('id', '=', shop_app_id.app.id)])
            API_KEY = app_id.api_key
            API_SECRET = app_id.secret_key
            api_version = app_id.api_version
            shop_url = self.shop_id.base_url
            TOKEN = shop_app_id.token
            shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)

            shopify_session = shopify.Session(shop_url, api_version, token=TOKEN)
            shopify.ShopifyResource.activate_session(shopify_session)

            pr = shopify.Product.find(limit=50)
            for product in pr:
                pro_vals = {
                    'name': product.title,
                    'price': product.variants[0].price,
                    'product_id': product.id,
                    'variant_id': product.variants,
                    # 'image_1920': product.images[0].src,
                    'shop_id': self.shop_id.id
                }
                check_product = self.env['shopify.product.load'].sudo().search(
                    [('product_id', '=', product.id)])
                if check_product:
                    check_product.sudo().write(pro_vals)
                else:
                    self.env['shopify.product.load'].sudo().create(pro_vals)

    def open_discount_check_product(self):
        self.update_shopify_product()

        discount_vals = {
            'discount_id': self.id,
        }
        new_discount = self.env['shopify.discount.choose.product'].sudo().create(discount_vals)

        if self.shop_id:
            pro_list = self.env['shopify.product.load'].sudo().search([('shop_id', '=', self.shop_id.id)], limit=50)
            create_pro_ids = []
            for pro in pro_list:
                create_pro_ids.append((0, 0, {
                    'discount_id': new_discount.id,
                    'product_id': pro.id,
                }))
            pro_vals = {
                'pro_ids': create_pro_ids
            }
            new_discount.write(pro_vals)

        view_id = self.env.ref('shopify_app.discount_choose_product_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Choose Product for Discount',
            'res_model': 'shopify.discount.choose.product',
            'views': [[view_id, 'form']],
            'res_id': new_discount.id,
            'target': 'new'
        }

    def open_customer(self):
        cus_list = self.env['res.partner'].search(
            [('shop_id', '=', self.shop_id.id), ('is_company', '=', False)], limit=50)

        for cus in cus_list:
            check_customer = self.env['shopify.discount.program.customer'].search(
                [('discount_id', '=', self.id), ('customer_id', '=', cus.id)])
            if not check_customer:
                cus_vals = {
                    'discount_id': self.id,
                    'customer_id': cus.id,
                }
                self.env['shopify.discount.program.customer'].create(cus_vals)


class ShopifyDiscountProgramProduct(models.Model):
    _name = "shopify.discount.program.product"

    discount_id = fields.Many2one('shopify.discount.program', string='Discount ID', ondelete='cascade')
    product_id = fields.Many2one('shopify.product.load', string='Product ID', ondelete='cascade')
    shop_product_id = fields.Char(related='product_id.product_id', string='Variant ID')
    name = fields.Char(related='product_id.name', string='Name')
    price = fields.Float(related='product_id.price')
    discount_amount = fields.Float(string='Discount Amount')
    check_product = fields.Boolean(string='Check')
    quantity = fields.Integer(string='Quantity', default=1)


class ShopifyDiscountProgramCustomer(models.Model):
    _name = "shopify.discount.program.customer"

    discount_id = fields.Many2one('shopify.discount.program', string='Discount ID', ondelete='cascade')
    customer_id = fields.Many2one('res.partner', string='Customer ID', ondelete='cascade')
    email = fields.Char(related='customer_id.email')
    check_person = fields.Boolean(string='Choose Person', default=True)
