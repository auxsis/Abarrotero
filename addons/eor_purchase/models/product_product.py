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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def insert_product_taxes(self):
        products = self.env['product.template']
        products_exent = products.search([('taxes_id.name', 'ilike', 'EXENTO')])
        # products_exent.write({'taxes_id': [(6, 0, [1, 13, 26])]})
        products_exent.write({'taxes_id': [(4, 26, 0)]})

        products_iva = products.search([('taxes_id.name', 'ilike', 'IVA(16%)')])
        # products_iva.write({'taxes_id': [(6, 0, [2, 14, 27])]})
        products_iva.write({'taxes_id': [(4, 27, 0)]})

        products_ieps = products.search([('taxes_id.name', 'ilike', 'IEPS')])
        # products_ieps.write({'taxes_id': [(6, 0, [24, 25, 40])]})
        products_ieps.write({'taxes_id': [(4, 40, 0)]})

