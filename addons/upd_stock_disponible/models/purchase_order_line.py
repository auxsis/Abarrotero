# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    stock_disponible = fields.Float(
        # related attrib has priority over computed attrib
        # To fix this we set related=None
        string="Stock disponible", related=None, store=True, compute='_compute_stock_disponible',
    )

    @api.depends('product_id')
    def _compute_stock_disponible(self):
        for prod_line in self:
            prod_line.stock_disponible = prod_line.product_id.qty_available

    @api.constrains('product_qty')
    def _check_product_qty(self):
        if self.product_qty <= 0:
            raise models.ValidationError(
                'El valor del campo cantidad en las lineas de productos debe de ser mayor que cero'
            )

