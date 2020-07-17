# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    maniobra_discount = fields.Float(string="Desc. Maniobra",  required=False, )
    flete_discount = fields.Float(string="Desc. Flete",  required=False, )
    plans_discount = fields.Float(string="Desc. Planes",  required=False, )
    total_extra_discount = fields.Float(string="Total Descuentos Extra", compute="compute_total_discount")

    @api.depends("maniobra_discount", "flete_discount", "plans_discount")
    def compute_total_discount(self):
        for invoice in self:
            invoice.total_extra_discount = sum(
                [invoice.maniobra_discount, invoice.flete_discount, invoice.plans_discount])

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'total_extra_discount')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        for invoice in self:
            invoice.amount_total += invoice.total_extra_discount


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    discount_2 = fields.Float(string='Discount 2')
