from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    # @api.multi
    # def invoice_validate(self):
    #     product_obj = self.env['product.product']
    #     # call the super methd here
    #     res = super(AccountInvoice, self).invoice_validate()
    #
    #     for invoice in self:
    #         if invoice.type in ('in_invoice', 'in_refund'):
    #             for line in invoice.invoice_line_ids:
    #                 if line.product_id and line.price_unit:
    #                     pass
    #                     #pr_id = product_obj.browse(line.product_id.id)
    #                     #pr_id.write({'standard_price': line.price_unit})
    #                     # line.product_id.sudo().standard_price = line.coste_neto
    #
    #     #return self.write({'state':'open'})
    #     return res