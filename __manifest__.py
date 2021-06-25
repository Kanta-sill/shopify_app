# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Shopify App',
    'version': '1.1',
    'summary': 'Invoices & Payments',
    'sequence': 10,
    'description': """
        Manage shop for Shopify connect
    """,
    'category': 'Accounting/Accounting',
    'website': 'https://www.odoo.com/',
    'images': [],
    'depends': ['base'],
    'data': [
        'security/shop_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/assets.xml',
        'views/shopify_app.xml',
        'views/shopify_shop.xml',
        'views/shopify_discount_program_view.xml',
        'views/shopify_dicount_preview.xml',
        'views/shopify_analytic_view.xml',
        'wizards/discount_choose_product_view.xml',
    ],
    'qweb': [
        'static/src/xml/qweb_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
