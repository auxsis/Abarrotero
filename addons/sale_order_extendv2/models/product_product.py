# -*- coding: utf-8 -*-
from odoo import models,api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.multi
    def name_get(self):
        if self._context.get('show_default_code'):
            result = []
            for product in self:
                result.append((product.id, "%s" % (product.default_code or product.name)))
            return result
        return super(ProductProduct,self).name_get()
    