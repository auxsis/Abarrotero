# -*- coding: utf-8 -*-
{
    'name': "Sale Order feature extend",

    'summary': """
        Sale Order line product name and description changed.""",

    'description': """
1. In SO or quotation when it's saved automatically fill expiration date to next day of quotation date.

2. When product is added in product column eliminate the name part of the product.

3. When product is added in description column eliminate the internal reference part.

4. When client is added add default discount to total discount.

    """,

    'author': "IT Admin",
    'website': "",
    'category': 'Sale',
    'version': '12.0',
    'depends': [
        'sale'
        ],
    'data': [
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
    ],

}
