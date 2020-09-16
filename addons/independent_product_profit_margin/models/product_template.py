# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    profit_margin = fields.Float(
        "Margen LP1 (%/$)",
        compute='_compute_profit_margin', inverse='_set_profit_margin', search='_search_profit_margin', store=True
    )
    profit_margin2 = fields.Float(
        "Margen LP2 (%/$)",
        compute='_compute_profit_margin2', inverse='_set_profit_margin2', search='_search_profit_margin2', store=True
    )

    @api.depends('product_variant_ids', 'product_variant_ids.profit_margin')
    def _compute_profit_margin(self):
        unique_variants = self.filtered(lambda t: len(t.product_variant_ids) == 1)  # t = template
        
        for template in unique_variants:
            template.profit_margin = template.product_variant_ids.profit_margin
        for template in (self - unique_variants):
            template.profit_margin = 0.0

    @api.one
    def _set_profit_margin(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.profit_margin = self.profit_margin

    def _search_profit_margin(self, operator, value):
        products = self.env['product.product'].search([('profit_margin', operator, value)], limit=None)
        return [('id', 'in', products.mapped('product_tmpl_id').ids)]

    @api.depends('product_variant_ids', 'product_variant_ids.profit_margin2')
    def _compute_profit_margin2(self):
        unique_variants = self.filtered(lambda t: len(t.product_variant_ids) == 1)  # t = template

        for template in unique_variants:
            template.profit_margin2 = template.product_variant_ids.profit_margin2
        for template in (self - unique_variants):
            template.profit_margin2 = 0.0
    
    @api.one
    def _set_profit_margin2(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.profit_margin2 = self.profit_margin2
    
    def _search_profit_margin2(self, operator, value):
        products = self.env['product.product'].search([('profit_margin2', operator, value)], limit=None)
        return [('id', 'in', products.mapped('product_tmpl_id').ids)]
