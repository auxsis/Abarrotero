# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class EorAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    maniobra_discount = fields.Float(string="Desc. Maniobra",  readonly=True)
    flete_discount = fields.Float(string="Desc. Flete",  readonly=True)
    plans_discount = fields.Float(string="Desc. Planes",  readonly=True)
    total_extra_discount = fields.Float(string="Total Descuentos Extra", compute="compute_total_discount")
    x_document_type = fields.Selection([('cdfi', 'CDFI'), ('remision', 'Remision')], string='Tipo documento',
                                       readonly=True, compute='compute_x_document_type', store=True)

    @api.depends('origin')
    def compute_x_document_type(self):
        for record in self:
            purchase_order = self.env['purchase.order'].search([('name', '=', record.origin)], limit=1)
            if purchase_order:
                document_type = purchase_order.x_document_type
                record['x_document_type'] = document_type

    @api.depends("maniobra_discount", "flete_discount", "plans_discount")
    def compute_total_discount(self):
        for invoice in self:
            invoice.total_extra_discount = sum(
                [invoice.maniobra_discount, invoice.flete_discount, invoice.plans_discount])

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'global_discount_type', 'global_order_discount', 'amount_tax', 'amount_untaxed', 'total_extra_discount')
    def _compute_amount(self):
        super(EorAccountInvoice, self)._compute_amount()
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total -= self.total_extra_discount
        self.amount_total_signed -= self.total_extra_discount * sign

    def _prepare_invoice_line_from_po_line(self, line):
        invoice_line = super(EorAccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        invoice_line["discount"] = line.desc1
        invoice_line["discount_2"] = line.desc2
        invoice_line['discount_type'] = 'percent'
        return invoice_line

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            quantity = 1.0
            if line.discount_type == 'fixed':
                price_unit = line.price_unit * line.quantity - (line.discount or 0.0) - (line.discount_2 or 0.0)
            else:
                quantity = line.quantity
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * (1 - (line.discount_2 or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, quantity, line.product_id,
                                                          self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(EorAccountInvoice, self).finalize_invoice_move_lines(move_lines)
        if self.total_extra_discount > 0:
            account_id = self.company_id.discount_extra_account_id
            if not account_id:
                raise UserError("Configure una cuenta de descuento para la compañía actual")
            move_lines.append((0, 0, {
                'date_maturity': False,
                'partner_id': self.partner_id.id,
                'name': 'Descuentos Extra',
                'debit': False,
                'credit': self.total_extra_discount,
                'account_id': account_id.id,
                'analytic_line_ids': [],
                'amount_currency': 0,
                'currency_id': False,
                'quantity': 1,
                'product_id': False,
                'product_uom_id': False,
                'analytic_account_id': False,
                'invoice_id': self.id,
                'tax_ids': False,
                'tax_line_id': False,
                'analytic_tag_ids': False,
            }))
            for line in move_lines:
                if line[2]['account_id'] == self.account_id.id and not line[2]['debit']:
                    line[2]['credit'] -= self.total_extra_discount
                    break
        return move_lines



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
