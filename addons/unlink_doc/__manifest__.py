# -*- coding: utf-8 -*-
{
    'name': "unlink_doc",

    'summary': """
    Agregar un permiso con la etiqueta "Suprimir documentos" en la pestaña de Permisos de acceso por usuario.
    """,

    'description': """
    Agregar un permiso con la etiqueta "Suprimir documentos" en la pestaña de Permisos de acceso por usuario.
    Al estar activado se puede suprimir o eliminar un documento.
    Al desactivar no puedan ver el botón de "Suprimir" y por lo tanto no podrán eliminar.
    """,

    'author': "Odoo Experts MX",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/groups.xml',
    ],

    "post_init_hook": "post_init_hook",
}
