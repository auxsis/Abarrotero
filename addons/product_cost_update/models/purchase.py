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
                intercompany_user = order.company_id.sudo().intercompany_user_id.id or False
                for line in order.order_line:
                    line.product_id.sudo(intercompany_user).standard_price = line.price_unit + line.price_tax / line.product_qty
        return res
