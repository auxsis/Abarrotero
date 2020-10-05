from odoo import fields, models


class MaintenanceEquipment (models.Model):
    _inherit = 'maintenance.equipment'

    name = fields.Char(translate=False)



