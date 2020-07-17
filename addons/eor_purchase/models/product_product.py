# -*- coding: utf-8 -*-

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def name_get(self):
        ref_only = self.env.context.get("ref_only")
        if ref_only:
            return [(product.id, '[%s]' % str(product.default_code) or '')for product in self]
        return super(ProductProduct, self).name_get()
