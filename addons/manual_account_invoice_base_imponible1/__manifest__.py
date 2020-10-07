# -*- coding: utf-8 -*-
{
    'name': "manual_account_invoice_base_imponible1",

    'summary': """
        Actualiza el campo "Precio" en las líneas de productos cuando se crea una factura de forma manual.
    """,

    'description': """
        Actualiza el campo "Precio" en las líneas de productos cuando se crea una factura de forma manual.
    """,

    'author': "Odoo Experts MX",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing Management',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'product_profit_margin'],
}
