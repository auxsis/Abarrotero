# -*- coding: utf-8 -*-
{
    'name': "Actualizar Stock Disponible",

    'summary': """
        Actualiza el Stock Disponible
        Usa como fórmula: "Stock Disponible" = "Prod Cant A Mano" + Cantidad
    """,

    'author': "Odoo Experts MX",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['eor_purchase'],
}
