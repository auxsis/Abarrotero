{
    'name': 'Purchase Modifications',
    'version': '1.0',
    'description': 'Modificaciones en OC - Odoo Grupo Guerrerense',
    'summary': 'Módulo de personalizaciones en las Órdenes de Compra',
    'author': 'Edgardo Ortiz <edgardoficial.yo@gmail.com>',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Odoo Experts',
    'depends': [
        'purchase',
        'discount_purchase_order',
    ],
    'data': [
        'views/purchase_view.xml',
        'views/purchase_templates.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'auto_install': True,
    'application': True,
    'installable': True
}