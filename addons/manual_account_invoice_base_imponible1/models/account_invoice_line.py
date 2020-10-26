# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    def _get_default_baseimponible1(self):
        if self.product_id:
            self.price_unit = self.product_id.base_imponible1

    price_unit = fields.Float(
        string='Unit Price', default=_get_default_baseimponible1, store=True, digits=dp.get_precision('Product Price')
    )

    @api.depends('product_id')
    def _compute_baseimponible1(self):
        for line in self.filtered(lambda l: not bool(l.origin)):
            line.price_unit = line.product_id.base_imponible1


