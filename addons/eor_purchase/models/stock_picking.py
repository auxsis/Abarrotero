# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
_logger = logging.getLogger("___________________________________________" + __name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        context = self.env.context
        PurchaseObj = self.env['purchase.order']
        order_id = context.get('active_id', None)
        model = context.get('active_model', False)

        #raise UserError(_("%s %s" % (order_id, model)))
        if order_id and model and model == 'purchase.order':
            purchase_id = PurchaseObj.browse(order_id)
            for line in self.move_ids_without_package:
                for order_line in purchase_id.order_line:
                    if not order_line.qty_received > 0:
                        # price_subtotal = line.product_uom_qty * order_line.price_unit
                        order_line.sudo().write({
                            'qty_received': line.quantity_done,
                            # 'line_sub_total': price_subtotal,
                            # 'price_subtotal': price_subtotal,
                        })
        return res