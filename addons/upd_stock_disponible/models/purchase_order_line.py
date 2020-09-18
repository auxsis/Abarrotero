# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    stock_disponible = fields.Float(
        # related attrib has priority over computed attrib
        # To fix this we set related=None
        string="Stock disponible", related=None, store=True, compute='_compute_stock_disponible',
    )

    @api.depends('product_qty')
    def _compute_stock_disponible(self):
        for prod_line in self:
            prod_line.stock_disponible = (
                prod_line.product_id.qty_available + prod_line.product_qty
                if prod_line.product_qty > 0 else
                0.0
            )

