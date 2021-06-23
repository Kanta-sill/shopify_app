import binascii
import json
import os
from random import randint

import shopify
import werkzeug
from werkzeug.utils import redirect

from odoo import http
from odoo.http import request


class MasterShopShopify(http.Controller):
    @http.route('/shopify/auth/mts', auth='public', website=False)
    def shopify_shop(self, **kwargs):
        if 'shop' in kwargs:
            app_current = request.env['shopify.app'].sudo().search([('app_name', '=', 'mts')], limit=1)
            API_KEY = app_current.api_key
            API_SECRET = app_current.secret_key
            api_version = app_current.api_version
            base_url = app_current.base_url
            shop_url = kwargs['shop']

            shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)

            state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
            redirect_uri = base_url + "/shopify/finalize/mts"
            scopes = ['read_orders', 'write_products', 'read_customers', 'write_script_tags', 'read_script_tags',
                      'read_themes', 'write_themes', 'read_discounts', 'write_discounts', 'read_price_rules',
                      'write_price_rules', 'unauthenticated_read_checkouts', 'read_draft_orders', 'write_draft_orders']
            newSession = shopify.Session(shop_url, api_version)
            auth_url = newSession.create_permission_url(scopes, redirect_uri)

            return werkzeug.utils.redirect(auth_url)

    @http.route('/shopify/finalize/mts', auth='public', website=False)
    def shopify_shop_final(self, **kwargs):
        app_current = request.env['shopify.app'].sudo().search([], limit=1)
        base_url = app_current.base_url
        api_version = app_current.api_version

        params = request.params
        shop_url = params['shop']
        session = shopify.Session(shop_url, api_version)

        access_token = session.request_token(params)  # request_token will validate hmac and timing attacks
        session = shopify.Session(shop_url, api_version, access_token)
        shopify.ShopifyResource.activate_session(session)

        theme_current = shopify.Theme.find(role='main')[0].id
        if theme_current:
            value = shopify.Asset.find('layout/theme.liquid', theme_id=theme_current).value

            index = value.find('''{{ content_for_header }}''')

            check_get_customer = value.find('''<!-- code get customer login information -->''')
            if check_get_customer == -1:
                parse_html = value[:index] + '''<!-- code get customer login information -->
    <script>
      window.customerId = "{{ customer.id }}";
    </script>
    <!-- code get customer login information -->
	''' + value[index:]
                shopify.Asset.create(dict(key="layout/theme.liquid", value=parse_html)).save()

        mk = randint(1000000000, 9999999999)
        shop = shopify.Shop.current()
        shopify_shop_current = request.env['shopify.shop'].sudo().search([("base_url", "=", shop_url)])
        if not shopify_shop_current:
            shop_vals = {
                'base_url': shop_url,
                'shop_owner': shop.shop_owner,
                'shop_currency': shop.currency,
                'password': mk
            }
            new_shop = request.env['shopify.shop'].sudo().create(shop_vals)

            request.env['shopify.shop.app'].sudo().create({
                'app': app_current.id,
                'shop': new_shop.id,
                'token': access_token
            })

            partner = request.env['res.partner'].sudo().create({
                'company_type': 'company',
                'name': shop.name,
                'street': shop.address1,
                'street2': shop.address2,
                'city': shop.city,
                'country_id': request.env['res.country'].sudo().search([('name', '=', 'Cuba')]).id,
                'zip': shop.zip,
                'email': shop.customer_email,
                'website': shop_url,
                'shop_id': new_shop.id
            })
            shop_user = request.env['res.users'].sudo().create({
                'login': shop_url,
                'password': mk,
                'active': 'true',
                'partner_id': partner.id,
            })
            group_current_shop = request.env.ref("shopify_app.group_current_shop")
            if group_current_shop:
                group_current_shop.sudo().write({
                    'users': [(4, shop_user.id)]
                })
            request.env['shopify.discount.preview'].sudo().create({
                'shop': new_shop.id,
            })
        else:
            shopify_shop_app_current = request.env['shopify.shop.app'].sudo().search(
                [('shop', '=', shopify_shop_current.id)])
            shopify_shop_app_current.sudo().write({
                'token': access_token
            })

        script_src = base_url + '/shopify_app/static/src/js/' + shop.name.replace(' ', '').lower() + '_script.js'
        existedScriptTags = shopify.ScriptTag.find(src=script_src)
        if not existedScriptTags:
            scriptTag = shopify.ScriptTag.create({
                "event": "onload",
                "src": script_src
            })

        mat_khau = request.env['shopify.shop'].sudo().search([("base_url", "=", shop_url)])
        db = http.request.env.cr.dbname
        request.env.cr.commit()
        uid = request.session.authenticate(db, shop_url, mat_khau.password)

        BundleMenu = request.env.ref('shopify_app.shop_app_root').id
        redirectUrl = base_url + '/web?#menu_id=' + str(BundleMenu)
        return werkzeug.utils.redirect(redirectUrl, 301)

    def check_product_ids(self, pro_list_a, pro_list_b):
        flag = True
        if len(pro_list_a) != len(pro_list_b):
            flag = False
        if flag == True:
            for pro in pro_list_a:
                if pro not in pro_list_b:
                    flag = False
                    break
        return flag

    @http.route('/shopify_data/fetch_variant/<string:customer_id>/<string:shop>', auth='public', type='json', cors='*',
                csrf=False)
    def odoo_fetch_variant(self, customer_id, shop, *kwargs):
        params = request.params
        shop_id = request.env['shopify.shop'].sudo().search([('base_url', '=', shop)])
        discount_product = request.env['shopify.discount.program'].sudo().search(
            [('shop_id', '=', shop_id.id)])
        shop_preview = request.env['shopify.discount.preview'].sudo().search([('shop', '=', shop_id.id)], limit=1)

        dis_program_product = []
        for discount_program in discount_product:
            # Check if customer is exist
            if discount_program.pro_ids and discount_program.cus_ids and customer_id != 'No Customer':
                customer_ids = []
                for customer in discount_program.cus_ids:
                    customer_ids.append(customer.cus_id)
                discount_amount = 0
                discount_name = []
                product_ids = []

                # Get valid discount for information
                for discount in discount_program.pro_ids:
                    for var in params['items']:
                        if discount.pro_id == str(var['product_id']) and \
                                var['quantity'] >= discount.quantity and discount.discount_amount > 0 \
                                and customer_id in customer_ids:
                            discount_amount += discount.discount_amount * var['quantity']
                            discount_name.append(var['title'])
                            product_ids.append(var['product_id'])
                            break

                # Add valid discount information to list dis_program_product
                if len(discount_program.pro_ids.ids) == len(product_ids):
                    dis_flag = True
                    for discount in dis_program_product:
                        if self.check_product_ids(discount['product_ids'], product_ids):
                            if discount_amount > discount['discount_amount']:
                                dis_program_product.remove(discount)
                                dis_program_product.append({
                                    'id': discount_program.id,
                                    'discount_program': discount_program.name,
                                    'products': discount_name,
                                    'discount_amount': discount_amount,
                                    'product_ids': product_ids
                                })
                                dis_flag = False
                                break
                    if dis_flag:
                        dis_program_product.append({
                            'id': discount_program.id,
                            'discount_program': discount_program.name,
                            'products': discount_name,
                            'discount_amount': discount_amount,
                            'product_ids': product_ids
                        })
        final_discount = 0
        for discount in dis_program_product:
            final_discount += discount['discount_amount']

        return {
            'discounts': dis_program_product,
            'final_discount': final_discount,
            'purchase': params['total_price'] - final_discount,
            'discount_color': shop_preview.discount_color,
            'amount_color': shop_preview.amount_color,
            'voucho_color': shop_preview.voucho_color
        }

    @http.route('/shopify_data/update_checkout/<string:shop>', auth='public', type='json', cors='*', csrf=False)
    def odoo_fetch_checkout(self, shop, *kwargs):
        shop_app_id = request.env['shopify.shop.app'].sudo().search([('shop', '=', shop)])
        app_id = request.env['shopify.app'].sudo().search([('id', '=', shop_app_id.app.id)])
        API_KEY = app_id.api_key
        API_SECRET = app_id.secret_key
        api_version = app_id.api_version
        TOKEN = shop_app_id.token

        shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)
        shopify_session = shopify.Session(shop, api_version, token=TOKEN)
        shopify.ShopifyResource.activate_session(shopify_session)

        params = request.params
        products = params['items']
        line_items = []
        for product in products:
            line_items.append({
                'variant_id': product['variant_id'],
                'quantity': product['quantity']
            })
        discount_program = params['discount_program']
        meta = shopify.Metafield.create({
            'namespace': 'draft_orders',
            'key': 'mastershop',
            'value': json.dumps(discount_program),
            'value_type': 'json_string',
        })
        applied_discount = {
            'title': 'Mastershop discount program',
            'description': 'SummerFestivalGift',
            'value_type': 'fixed_amount',
            'value': params['discount_value']
        }

        new_checkout = False
        if meta:
            note_attributes = [{
                'name': 'mastershop_checkout',
                'value': meta.id
            }]
            vals = {
                'line_items': line_items,
                'applied_discount': applied_discount,
                'customer': {
                    'id': params['customer_id']
                },
                'note_attributes': note_attributes
            }
            new_checkout = shopify.DraftOrder.create(vals)

        return new_checkout.invoice_url
