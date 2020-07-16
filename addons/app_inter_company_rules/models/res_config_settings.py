# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_validation = fields.Selection([('draft', 'draft'), ('validated', 'confirmed')])
