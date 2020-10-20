# -*- coding: utf-8 -*-
{
    'name': 'Descuentos por unidad PACK',
    'description': "descuentos en productos.",
    'author': "",
    'website': "",
    'summary': "descuentos en productos.",
    'version': '0.1',
    "license": "OPL-1",
    'support': '',
    'category': 'Productos',
    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'installable': True,
}
