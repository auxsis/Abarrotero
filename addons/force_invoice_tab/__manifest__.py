# -*- coding: utf-8 -*-
{
    'name': "force_invoice_tab",

    'summary': """
    Cambia la pestaña por defecto según 2 condiciones (Ver Descripción)
    """,

    'description': """
        Al crear una factura desde el módulo Facturación/Cont. mostrar como pantalla principal la pestaña "CFDI 3.3".
        Las facturas (documentos) ya generados, al abrir que se muestre como pantalla principal
         la pestaña "Líneas de factura".
    """,

    'author': "Odoo Experts MX",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['cdfi_invoice'],

    # always loaded
    'data': [
        'views/views.xml',
        # 'views/templates.xml',
    ],
}
