# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    profit_margin = fields.Float(
        "Margen LP1 (%/$)", company_dependent=True, digits=dp.get_precision('Product Price')
    )
    profit_margin2 = fields.Float(
        "Margen LP2 (%/$)", company_dependent=True, digits=dp.get_precision('Product Price')
    )
