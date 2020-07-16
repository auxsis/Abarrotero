# -*- coding: utf-8 -*-
from odoo import models,api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine,self).product_id_change()
        if self.product_id:
            #name = self.name
            #self.name = name[name.find(']')+1:].strip()
            #self.product_id = self.product_id.default_code
            self.name = self.product_id.name
        return res
    