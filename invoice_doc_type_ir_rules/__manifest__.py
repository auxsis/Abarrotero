# -*- coding: utf-8 -*-
{
    'name': "invoice_doc_type_ir_rules",

    'summary': """
        Agrega reglas de filtrado de registros para las facturas de los proveedores según el tipo de documento. 
    """,

    'description': """
        Agrega reglas de filtrado de registros para las facturas de los proveedores según el tipo de documento.
    """,

    'author': "Odoo Experts MX",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing Management',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['eor_purchase'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/account_rules.xml',
    ],
}
