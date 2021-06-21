from odoo import api, fields, models, _, tools
import shopify

from odoo.exceptions import UserError


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

    def get_authenticate_shopify(self):
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
        return shopify

    def open_discount_check_product(self):
        discount_vals = {
            'discount_id': self.id,
        }
        new_discount = self.env['shopify.discount.choose.product'].sudo().create(discount_vals)
        if self.shop_id:
            self.get_authenticate_shopify()
            products = shopify.Product.find(limit=50)
            create_pro_ids = []
            for product in products:
                create_pro_ids.append((0, 0, {
                    'discount_id': new_discount.id,
                    'pro_id': product.id,
                    'name': product.title,
                }))
            if create_pro_ids:
                pro_vals = {
                    'pro_ids': create_pro_ids
                }
                new_discount.sudo().write(pro_vals)

        view_id = self.env.ref('shopify_app.discount_choose_product_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Choose Product for Discount'),
            'view_mode': 'form',
            'res_model': 'shopify.discount.choose.product',
            'target': 'new',
            'res_id': new_discount.id,
            'views': [[view_id, 'form']],
        }

    @api.depends('shop_id')
    def open_customer(self):
        if self.shop_id:
            self.get_authenticate_shopify()
            customers = shopify.Customer.search()
            for customer in customers:
                check_customer = self.env['shopify.discount.program.customer'].search(
                    [('discount_id', '=', self.id), ('cus_id', '=', customer.id)])
                name = customer.first_name + ' ' + customer.last_name
                cus_vals = {
                    'discount_id': self.id,
                    'cus_id': customer.id,
                    'name': name,
                    'email': customer.email
                }
                if not check_customer:
                    self.env['shopify.discount.program.customer'].sudo().create(cus_vals)
                else:
                    check_customer.sudo().write(cus_vals)
        else:
            raise UserError(_('You must add shop first.'))


class ShopifyDiscountProgramProduct(models.Model):
    _name = "shopify.discount.program.product"

    discount_id = fields.Many2one('shopify.discount.program', string='Discount ID', ondelete='cascade')
    pro_id = fields.Char(string='Pro ID')
    name = fields.Char(string='Name')
    discount_amount = fields.Float(string='Discount Amount')
    check_product = fields.Boolean(string='Check')
    quantity = fields.Integer(string='Quantity', default=1)


class ShopifyDiscountProgramCustomer(models.Model):
    _name = "shopify.discount.program.customer"

    discount_id = fields.Many2one('shopify.discount.program', string='Discount ID', ondelete='cascade')
    cus_id = fields.Char(string='Cus ID')
    name = fields.Char(string='Name')
    email = fields.Char(string='Email')
    check_person = fields.Boolean(string='Choose Person', default=True)
