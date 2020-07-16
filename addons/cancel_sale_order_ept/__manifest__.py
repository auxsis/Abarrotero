{
   
   # App information
    'name': 'Cancel Sales Order In Odoo',
    'version': '12.0',
    'category': 'Sales',
    'summary' : 'Allow to cancel such  Sales Order  whose Delivery is validated / done.',
    'license': 'OPL-1',
    
       
    
    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
   
   
   
   
   # Dependencies
    'depends': ['sale_management',
        'cancel_stock_picking_ept',
    ],
    
    # Views
    'data': [
        'view/sale_order.xml'
    ],
    
    
    
    # Odoo Store Specific
    'images': ['static/description/Cancel-Sales-Order-in-Odoo-Cover.jpg'],
    'live_test_url' : 'https://www.emiprotechnologies.com/free-trial?app=cancel-sale-order-ept&version=12&edition=enterprise',
    'price': '40' ,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}
