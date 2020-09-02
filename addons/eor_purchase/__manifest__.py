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
        'account',
        'purchase',
        'discount_purchase_order',
        'product_profit_margin',
    ],
    'data': [
        'views/purchase_view.xml',
        'views/purchase_templates.xml',
        'views/account_invoice.xml',
        'views/product_template.xml',
        'views/stock_backorder_confirmation.xml',
        'views/res_company.xml',
        'report/purchase_order.xml',
        'report/purchase_quotation.xml',
        'data/mail_data.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'auto_install': True,
    'application': True,
    'installable': True
}