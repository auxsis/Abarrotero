# -*- coding: utf-8 -*-

from odoo import models, fields


class FraccionArancelaria(models.Model):
    _name = 'catalogos.fraccionarancelaria'
    _rec_name = "c_fraccionarancelaria"

    c_fraccionarancelaria = fields.Char(string='Fracción Arancelaria')
    descripcion = fields.Char(string='Descripción')
