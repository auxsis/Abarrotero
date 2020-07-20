# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if res:
            for order in self:
                # intercompany_user = order.company_id.sudo().intercompany_user_id.id or False
                for line in order.order_line:
                    line.product_id.write({"standard_price": line.coste_neto})
                    # line.product_id.sudo(intercompany_user).standard_price = line.price_unit + line.price_tax / line.product_qty
        return res

    def fix_standard_price(self):
        order_ids = self.env['purchase.order'].search([('state', '=', 'purchase')], order='id asc')
        for order in order_ids:
            for line in order.order_line:
                line.product_id.write({"standard_price": line.coste_neto})

    def fix_seller_price(self):
        order_ids = self.env['purchase.order'].search([('state', '=', 'purchase')], order='id asc')
        for order in order_ids:
            for line in order.order_line:
                seller = line.product_id.seller_ids.filtered(lambda sel: sel.name.id == order.partner_id.id)
                if seller:
                    print("Here")
                seller.write({"price": line.price_unit})
