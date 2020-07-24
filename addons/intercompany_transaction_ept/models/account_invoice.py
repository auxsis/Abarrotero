from odoo import api, models, fields , _

class AccountInvoice(models.Model):
    
    _inherit = 'account.invoice'
    _description = 'Account Invoice'

        
    intercompany_transfer_id = fields.Many2one('inter.company.transfer.ept', string="ICT", copy=False)
    amount_transfer_fee = fields.Float("Monto Costo de Transf.", related="intercompany_transfer_id.amount_transfer_fee", store=True)
    
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
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        self.update({
            'amount_total': self.amount_total + self.amount_transfer_fee,
        })