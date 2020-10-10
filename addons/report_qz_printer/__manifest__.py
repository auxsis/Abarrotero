# -*- coding: utf-8 -*-
{
    'name': "report_qz_printer",

    'summary': """
        Imprime documentos sin tener que descargar el PDF, usando QZ.
    """,

    'description': """
        Imprime documentos sin tener que descargar el PDF, usando QZ.
    """,

    'author': "Odoo Experts MX",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Printer',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'purchase'],

    # always loaded
    'data': [
        'views/res_company_view.xml',
        'views/template.xml',
    ],
}
