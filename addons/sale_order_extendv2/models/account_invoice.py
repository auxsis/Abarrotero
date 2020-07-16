# -*- coding: utf-8 -*-
from odoo import models,api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine,self)._onchange_product_id()
        if self.product_id:
            self.name = self.product_id.name
        return res