# -*- coding: utf-8 -*-
{
    'name': "independent_product_profit_margin",

    'summary': """
        Set the Price List based on Profit Margin.
        One per Company
    """,

    'description': """
        Set the Price List based on Profit Margin.
        One per Company
    """,

    'author': "Juan Carlos Fernández Hernández",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'product',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['product_profit_margin'],

    "post_init_hook": "post_init_hook",
    "pre_init_hook": "pre_init_hook",
}
