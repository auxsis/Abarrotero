from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    discount_extra_account_id = fields.Many2one('account.account', string="Cuenta para Descuentos Extras")