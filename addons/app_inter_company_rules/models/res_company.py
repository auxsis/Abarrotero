# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import Warning


class res_company(models.Model):
    _inherit = 'res.company'

    auto_validation = fields.Selection([('draft', 'draft'), ('validated', 'confirmed')])
