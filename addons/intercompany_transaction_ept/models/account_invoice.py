from odoo import api, models, fields, _
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    
    _inherit = 'account.invoice'
    _description = 'Account Invoice'

        
    intercompany_transfer_id = fields.Many2one('inter.company.transfer.ept', string="ICT", copy=False)
    transfer_fee_id = fields.Float("Costo de Transf. (%)", related="intercompany_transfer_id.transfer_fee")
    amount_transfer_fee = fields.Float("Monto Costo de Transf.", related='intercompany_transfer_id.amount_transfer_fee')
    
    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        order_id = self.env['sale.order'].search([('name', '=', res.origin)])
        if not order_id:
            order_id = self.env['purchase.order'].search([('name', '=', res.origin)])
        if order_id and order_id.intercompany_transfer_id:
            res.intercompany_transfer_id = order_id.intercompany_transfer_id.id
        return res

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'global_discount_type', 'global_order_discount', 'amount_tax', 'amount_untaxed',
                 'total_extra_discount', 'transfer_fee_id')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.update({
            'amount_total': self.amount_total + self.amount_transfer_fee,
            'amount_total_signed': self.amount_total_signed + self.amount_transfer_fee * sign,
        })

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        """ finalize_invoice_move_lines(move_lines) -> move_lines

            Hook method to be overridden in additional modules to verify and
            possibly alter the move lines to be created by an invoice, for
            special cases.
            :param move_lines: list of dictionaries with the account.move.lines (as for create())
            :return: the (possibly updated) final move_lines to create for this invoice
        """
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        if self.type in (['out_invoice']):
            if self.amount_transfer_fee > 0:
                journal_id = self.company_id.sale_journal
                if not journal_id:
                    raise UserError("Registre un diario de ventas ICT para esta compañía")
                move_lines.append((0, 0, {
                    'date_maturity': False,
                    'partner_id': self.partner_id.id,
                    'name': 'Monto de Transferencia Intercompañía',
                    'debit': False,
                    'credit': self.amount_transfer_fee,
                    'account_id': journal_id.default_credit_account_id.id,
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
                    if line[2]['account_id'] == self.account_id.id and not line[2]['credit']:
                        line[2]['debit'] += self.amount_transfer_fee
                        break

        if self.type in (['in_invoice']):
            if self.amount_transfer_fee > 0:
                journal_id = self.company_id.purchase_journal
                if not journal_id:
                    raise UserError("Registre un diario de compras ICT para esta compañía")
                move_lines.append((0, 0, {
                    'date_maturity': False,
                    'partner_id': self.partner_id.id,
                    'name': 'Monto de Transferencia Intercompañía',
                    'debit': self.amount_transfer_fee,
                    'credit': False,
                    'account_id': journal_id.default_debit_account_id.id,
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
                        line[2]['credit'] += self.amount_transfer_fee
                        break
        return move_lines





