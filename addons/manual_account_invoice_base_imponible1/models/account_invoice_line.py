# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    price_unit = fields.Float(string='Unit Price', compute="_compute_baseimponible1", store=True)

    @api.depends('product_id', 'product_id.base_imponible1')
    def _compute_baseimponible1(self):
        for line in self.filtered(lambda l: not bool(l.origin)):
            line.price_unit = line.product_id.base_imponible1
