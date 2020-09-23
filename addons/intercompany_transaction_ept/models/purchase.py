# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError

from lxml import etree
import simplejson


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
        if self.company_id != self.env.user.company_id:
            raise ValidationError("Lo sentimos, la compañía desde la que intenta generar la factura no se corresponde con la compañía de la orden.")
        res = super(PurchaseOrder, self).action_view_invoice()
        if res and self.intercompany_transfer_id:
            if res.get('context') == None:
                res['context'] = {}
            res['context'].update({
                'default_intercompany_transfer_id': self.intercompany_transfer_id.id,
            })
        return res

    @api.multi
    def button_confirm(self):
        if self.company_id != self.env.user.company_id:
            raise ValidationError("Lo sentimos, no puede confirmar la orden, la compañía actual no se corresponde con la compañía de la orden.")
        return super(PurchaseOrder, self).button_confirm()

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                     submenu=submenu)
        if self.env.context.get('readonly_purchase'):  # Check for context value
            doc = etree.XML(res['arch'])  # Get the view architecture of record
            if view_type == 'form':  # Applies only if it is form view
                for node in doc.xpath("//field"):  # Get all the fields navigating through xpath
                    modifiers = simplejson.loads(node.get("modifiers"))  # Get all the existing modifiers of each field
                    modifiers['readonly'] = True  # Add readonly=True attribute in modifier for each field
                    node.set('modifiers',
                             simplejson.dumps(modifiers))  # Now, set the newly added modifiers to the field
                for node in doc.xpath("//header/button"):
                    modifiers = {'invisible': True}
                    node.set('modifiers', simplejson.dumps(modifiers))
                res['arch'] = etree.tostring(doc)  # Update the view architecture of record with new architecture
        return res