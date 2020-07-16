from odoo import api, fields, models, _

class sale_order(models.Model):
    _inherit = "sale.order"

    # cancel the sale order than automatic cancel the invoice and picking
    @api.multi
    def action_cancel(self):
        stock_picking_ids = self.env['stock.picking'].search([('sale_id', '=', self.id),('state','!=','cancel')])
        if stock_picking_ids:
            return_ids = self.env['stock.return.picking'].search([('picking_id', '=', stock_picking_ids.ids)])
            if return_ids:
                for return_id in return_ids:
                    return_id.picking_id.move_lines.stock_quant_update_ept()
            else:
                dict = {}
                customer_picking = stock_picking_ids.filtered(lambda x: x.picking_type_id.code == 'outgoing')
                if customer_picking:
                    # list_customer_picking = []
                    # for customer in customer_picking:
                    #     list_customer_picking.append(customer)
                    dict.update({1:customer_picking})
                    output_picking = stock_picking_ids.filtered(lambda x :customer_picking[0].location_id.id == x.location_dest_id.id)
                    if output_picking:
                        dict.update({2:output_picking})
                        stock_picking = stock_picking_ids.filtered(lambda x:output_picking[0].location_id.id == x.location_dest_id.id)
                        if stock_picking:
                            dict.update({3:stock_picking})

                if dict.get(1,False):
                    for cancel in dict.get(1):
                        cancel.move_lines.stock_quant_update_ept()
                if dict.get(2,False):
                    for cancel in dict.get(2):
                        cancel.move_lines.stock_quant_update_ept()
                if dict.get(3,False):
                    for cancel in dict.get(3):
                        cancel.move_lines.stock_quant_update_ept()

                # for internal_pick in stock_picking_ids.filtered(lambda x: x.picking_type_id.code == 'internal' and x.state != 'cancel' and x.location_id.id == self.env.ref('stock.location_pack_zone').id):
                #     internal_pick.move_lines.stock_quant_update_ept()
                # if stock_picking_id != 'cancel':
                #     stock_picking_id.move_lines.stock_quant_update_ept()

        if self.invoice_ids:
            for invoice_id in self.invoice_ids:
                if invoice_id.state == 'paid':
                    invoice_id.move_id.line_ids.sudo().remove_move_reconcile()
                    invoice_id.action_cancel()
                else:
                    invoice_id.action_cancel()
        return super(sale_order, self).action_cancel()

    # if set to quotation than cancel the automatic picking  and invoices
    @api.multi
    def action_draft(self):
        self.action_cancel()
        return super(sale_order, self).action_draft()