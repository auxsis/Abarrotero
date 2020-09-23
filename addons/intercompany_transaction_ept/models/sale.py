from odoo import api, fields, models, _

from lxml import etree
import simplejson


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'
    
    intercompany_transfer_id = fields.Many2one('inter.company.transfer.ept', string="ICT", copy=False)
    transfer_fee_id = fields.Float("Costo de Transf. (%)", related="intercompany_transfer_id.transfer_fee")
    amount_transfer_fee = fields.Float("Monto Costo de Transf.", compute='_amount_all')


    """
    This Method is used to invoice journal issue when it is creating time(as breadcrumb)
    """
    @api.multi
    def _prepare_invoice(self):
        if self.intercompany_transfer_id:
            journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
            vals = super(SaleOrder, self.with_context({'journal_id':journal_id}))._prepare_invoice()
            return vals
        else:
            vals = super(SaleOrder, self)._prepare_invoice()
            return vals

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO including Transfer Fee.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_transfer_fee = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            if order.transfer_fee_id:
                amount_transfer_fee = (amount_untaxed + amount_tax) * order.transfer_fee_id / 100

            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax + amount_transfer_fee,
                'amount_transfer_fee': amount_transfer_fee,
            })

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                     submenu=submenu)
        if self.env.context.get('readonly_sale'):  # Check for context value
            doc = etree.XML(res['arch'])  # Get the view architecture of record
            if view_type == 'form':  # Applies only if it is form view
                for node in doc.xpath("//field"):  # Get all the fields navigating through xpath
                    modifiers = simplejson.loads(node.get("modifiers"))  # Get all the existing modifiers of each field
                    modifiers['readonly'] = True  # Add readonly=True attribute in modifier for each field
                    node.set('modifiers',
                             simplejson.dumps(modifiers))  # Now, set the newly added modifiers to the field
                for node in doc.xpath("//header/button"):
                    # modifiers = simplejson.loads(node.get("modifiers"))
                    modifiers = {'invisible': True}
                    node.set('modifiers', simplejson.dumps(modifiers))
                res['arch'] = etree.tostring(doc)  # Update the view architecture of record with new architecture
        return res
