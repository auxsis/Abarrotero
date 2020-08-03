{
    'name': 'Sale utils',
    'version': '1.0',
    'description': 'Sale utils',
    'summary': '',
    'author': 'Edgardo Ortiz <edgardoficial.yo@gmail.com>',
    'website': 'https://github.com/eortizromero',
    'license': 'LGPL-3',
    'category': 'Odoo Experts',
    'depends': [
        'sale',
        'cdfi_invoice',
    ],
    'data': [
        'views/sale_view.xml',
        'report/sale_order.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}