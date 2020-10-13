# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ClaveProdServ(models.Model):
    _name = 'catalogos.claveprodserv'
    _rec_name = "descripcion"

    c_claveprodserv = fields.Char(string='Clave de Producto o servicio')
    descripcion = fields.Char(string='Descripción')

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', ('c_claveprodserv', operator, name), ('descripcion', operator, name)]
        return super(ClaveProdServ, self).search(domain, limit=limit).name_get()