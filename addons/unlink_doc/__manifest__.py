# -*- coding: utf-8 -*-
{
    'name': "unlink_doc",

    'summary': """
    Agregar tres permisos:
        "Suprimir/Eliminar Facturas"
        "Suprimir/Eliminar Compras"
        "Suprimir/Eliminar Ventas"
     
    Estos desactivan/activan la posibilidad de eliminar/suprimir los documentos respectivos.
    """,

    'description': """
    Agregar tres permisos:
        "Suprimir/Eliminar Facturas"
        "Suprimir/Eliminar Compras"
        "Suprimir/Eliminar Ventas"
     
    Estos desactivan/activan la posibilidad de eliminar/suprimir los documentos respectivos.
    """,

    'author': "Odoo Experts MX",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'sale', 'account'],

    # always loaded
    'data': [
        'security/groups.xml',
    ],

    "post_init_hook": "post_init_hook",
}
