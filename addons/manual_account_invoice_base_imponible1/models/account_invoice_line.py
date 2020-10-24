# -*- coding: utf-8 -*-

from odoo import models, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('price_unit')
    def _set_baseimponible1(self):
        if not self.origin:
            base_imponible1 = self.product_id.base_imponible1
            if self.price_unit != base_imponible1:
                self.price_unit = base_imponible1
