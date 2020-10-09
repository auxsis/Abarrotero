# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    price_unit = fields.Float(
        string='Unit Price', compute="_compute_baseimponible1", store=True, digits=dp.get_precision('Product Price')
    )

    @api.onchange('price_unit')
    def _set_baseimponible1(self):
        base_imponible1 = self.product_id.base_imponible1
        if self.price_unit != base_imponible1:
            self.price_unit = base_imponible1

    @api.depends('product_id')
    def _compute_baseimponible1(self):
        for line in self.filtered(lambda l: not bool(l.origin)):
            line.price_unit = line.product_id.base_imponible1
