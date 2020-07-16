{
    # App information
    'name': 'Cancel Stock Picking',
    'version': '12.0',
    'category': 'stock',
    'summary' : 'Allow to cancel Processed Picking.',
    'license': 'OPL-1',
   
    
     # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    
  
    
    # Dependencies
       
    'depends': ['stock','account_cancel'],
    
    # Views
    
    'data': [
     'view/stock_picking.xml',
     'view/stock_location.xml'
    ],
    'demo': [
    ],
    
    
     # Odoo Store Specific
    'images': ['static/description/Cancel-&-Reset-Picking-to-Draft-In-Odoo-cover.jpg'],
     'live_test_url' : 'https://www.emiprotechnologies.com/free-trial?app=cancel-stock-picking-ept&version=12&edition=enterprise',
    'price': '59' ,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,

}
