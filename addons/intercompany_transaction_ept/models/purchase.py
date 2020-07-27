from odoo import fields, api, models , _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    transfer_fee_id = fields.Float("Costo de Transf. (%)", related="intercompany_transfer_id.transfer_fee")
    amount_transfer_fee = fields.Float("Monto Costo de Transf.", compute='_amount_all')
    intercompany_transfer_id = fields.Many2one('inter.company.transfer.ept', string="ICT", copy=False)


    @api.depends('order_line.price_total')
    def _amount_all(self):
        super(PurchaseOrder, self)._amount_all()
        for order in self:
            if order.transfer_fee_id:
                amount_transfer_fee = (order.amount_untaxed + order.amount_tax) * order.transfer_fee_id / 100

                order.update({
                    'amount_total': order.amount_total + amount_transfer_fee,
                    'amount_transfer_fee': amount_transfer_fee,
                })

    @api.multi
    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        if res and self.intercompany_transfer_id:
            if res.get('context') == None:
                res['context'] = {}
            res['context'].update({
                'default_intercompany_transfer_id': self.intercompany_transfer_id.id
            })
        return res
