from odoo import fields, models, api, _

from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = "res.company"
    _description = 'Res Company'

    intercompany_user_id = fields.Many2one('res.users', string="Intercompany User")    
    sale_journal = fields.Many2one('account.journal', string="Sale Journal")
    purchase_journal = fields.Many2one('account.journal', string="Purchase Journal")

    @api.multi
    @api.constrains('sale_journal', 'purchase_journal')
    def constrains_sale_purchase_journal(self):
        for company in self:
            if not company.sale_journal.company_id.id == company.id:
                raise ValidationError(_("The sales journal does not belong to the company."))
            if not company.purchase_journal.company_id.id == company.id:
                raise ValidationError(_("The purchase journal does not belong to the company."))