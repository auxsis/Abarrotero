# -*- coding: utf-8 -*-

import json
import logging

from odoo import _, api, fields, models
from odoo.tools import date_utils

_logger = logging.getLogger('-----------------------------------------------------------------------' + __name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.tax_id', 'amount_tax')
    def _compute_taxes_widget(self):
        for order in self:
            taxes_vals = order._get_taxes_JSON_values()
            if taxes_vals:
                inf = {
                    'title': _('Hola Mundo'),
                    'content': taxes_vals
                }
                order.taxes_widget = json.dumps(inf, default=date_utils.json_default)
            else:
                order.taxes_widget = json.dumps(False)

    def _get_taxes_JSON_values(self):
        taxes_vals = []
        order_line = self.order_line.filtered(lambda line: line.tax_id != False)
        for tax_id in self.mapped('order_line.tax_id'):
            taxes_vals.append({
                'name': tax_id.name,
                'currency': self.currency_id.symbol,
                'digits': [69, self.currency_id.decimal_places],
                'amount_tax': sum([self.currency_id.round(l.price_tax) for l in
                                   self.order_line.filtered(lambda t: t.tax_id.id == tax_id.id)])
            })

        return taxes_vals

    taxes_widget = fields.Text(compute="_compute_taxes_widget", string="Impuestos")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('price_unit', 'price_tax')
    def _compute_price(self):
        for line in self:
            price_unit = line.price_unit
            price_tax = 0.00
            if line.product_uom_qty > 0:
                price_tax = line.price_tax / line.product_uom_qty

            if line.price_unit_tax <= 0:
                line.price_unit_tax = price_unit + price_tax
            if line.product_id.units_pack > 0:
                line.precio_x_pieza = line.price_unit_tax / line.product_id.units_pack
            
    
    @api.depends('product_id')
    def _compute_stock_available(self):
        for line in self:
            line.stock_disponible = line.product_id.qty_available

    stock_disponible = fields.Float(string="Stock disponible", compute="_compute_stock_available")
    precio_x_pieza = fields.Monetary(string='Precio por pieza', compute='_compute_price')
    price_unit_tax = fields.Float(compute='_compute_price', string="Precio Neto")
