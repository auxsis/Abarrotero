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