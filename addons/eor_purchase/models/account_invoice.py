# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EorAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    maniobra_discount = fields.Float(string="Desc. Maniobra",  readonly=True)
    flete_discount = fields.Float(string="Desc. Flete",  readonly=True)
    plans_discount = fields.Float(string="Desc. Planes",  readonly=True)
    total_extra_discount = fields.Float(string="Total Descuentos Extra", compute="compute_total_discount")

    @api.depends("maniobra_discount", "flete_discount", "plans_discount")
    def compute_total_discount(self):
        for invoice in self:
            invoice.total_extra_discount = sum(
                [invoice.maniobra_discount, invoice.flete_discount, invoice.plans_discount])

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'global_discount_type', 'global_order_discount', 'total_extra_discount')
    def _compute_amount(self):
        super(EorAccountInvoice, self)._compute_amount()
        self.amount_total -= self.total_extra_discount

    def _prepare_invoice_line_from_po_line(self, line):
        invoice_line = super(EorAccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        invoice_line["discount"] = line.desc1
        invoice_line["discount_2"] = line.desc2
        invoice_line['discount_type'] = 'percent'
        return invoice_line


class EorAccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    discount_2 = fields.Float(string='Disc2(%)')

    @api.one
    @api.depends('price_unit', 'discount', 'discount_type', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice')
    def _compute_price(self):
        super(EorAccountInvoiceLine, self)._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        quantity = 1.0
        subTotalAmount = 0.0
        if self.discount_type == 'fixed':
            price = self.price_unit * self.quantity - self.discount - self.discount_2 or 0.0
            subTotalAmount = price
        else:
            quantity = self.quantity
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0) * (1 - (self.discount_2 or 0.0) / 100.0)
            subTotalAmount = self.quantity * price
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(
                price, currency, quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        if self.discount_type == 'fixed':
            self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else price
        else:
            self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id.date_invoice).compute(price_subtotal_signed,
                                                           self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
