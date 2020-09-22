# -*- coding: utf-8 -*-

from odoo import models, fields


class Municipio(models.Model):
    _name = 'catalogos.municipio'
    _rec_name = "descripcion"

    c_municipio = fields.Char(string='Clave de Municipio')
    c_estado = fields.Char(string='Clave Estado')
    descripcion = fields.Char(string='Descripción')
