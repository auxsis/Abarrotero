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
    def update_product_taxes(self):

        products = self.env['product.template']
        taxes = self.env['account.tax']

        # ------------------------------EXENTOS-------------------------------
        # ------Sale---------
        customer_tax_ids = taxes.sudo().search([('type_tax_use', '=', 'sale'), ('name', 'ilike', 'EXENTO')])
        products_exent = products.sudo().search([('taxes_id.name', 'ilike', 'EXENTO')])
        products_exent.sudo().write({'taxes_id': [(6, 0, customer_tax_ids.mapped('id'))]})

        # -----Purchase------
        supplier_tax_ids = taxes.sudo().search([('type_tax_use', '=', 'purchase'), ('name', 'ilike', 'EXENTO')])
        products_exent_supplier = products.sudo().search([('supplier_taxes_id.name', 'ilike', 'EXENTO')])
        products_exent_supplier.sudo().write({'supplier_taxes_id': [(6, 0, supplier_tax_ids.mapped('id'))]})

        # --------------------------------IVA---------------------------------
        # ------Sale---------
        customer_tax_ids = taxes.sudo().search([('type_tax_use', '=', 'sale'), ('name', 'ilike', 'IVA(16%)')])
        products_iva = products.sudo().search([('taxes_id.name', 'ilike', 'IVA(16%)')])
        products_iva.sudo().write({'taxes_id': [(6, 0, customer_tax_ids.mapped('id'))]})

        # -----Purchase------
        supplier_tax_ids = taxes.sudo().search([('type_tax_use', '=', 'purchase'), ('name', 'ilike', 'IVA(16%)')])
        products_iva_supplier = products.sudo().search([('supplier_taxes_id.name', 'ilike', 'IVA(16%)')])
        products_iva_supplier.sudo().write({'supplier_taxes_id': [(6, 0, supplier_tax_ids.mapped('id'))]})

        # -------------------------------IEPS----------------------------------
        # ------Sale---------
        customer_tax_ids = taxes.sudo().search([('type_tax_use', '=', 'sale'), ('name', 'ilike', 'IEPS')])
        products_ieps = products.sudo().search([('taxes_id.name', 'ilike', 'IEPS')])
        products_ieps.sudo().write({'taxes_id': [(6, 0, customer_tax_ids.mapped('id'))]})

        # -----Purchase------
        supplier_tax_ids = taxes.sudo().search([('type_tax_use', '=', 'purchase'), ('name', 'ilike', 'IEPS')])
        products_ieps_supplier = products.sudo().search([('supplier_taxes_id.name', 'ilike', 'IEPS')])
        products_ieps_supplier.sudo().write({'supplier_taxes_id': [(6, 0, supplier_tax_ids.mapped('id'))]})

