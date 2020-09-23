# -*- coding: utf-8 -*-
# unlink_doc
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    # Get Environment
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Unset unlink permissions on all models
    for model_access in env['ir.model.access'].search([
        ('perm_unlink', '=', True),
    ]):
        if model_access.perm_unlink:
            model_access.perm_unlink = False

    # Get group named "Suprimir/Eliminar Documentos"
    unlink_res_group = env['res.groups'].search([
        ('name', '=', 'Suprimir/Eliminar Documentos'),
    ]).ensure_one()

    # Add unlink permissions on all models for security group "Suprimir/Eliminar Documentos"
    env['ir.model.access'].create([
        {
            'name': f'{ir_model.model}.perm_unlink', 'model_id': ir_model.id,
            'group_id': unlink_res_group.id,
            'perm_read': False, 'perm_write': False, 'perm_create': False, 'perm_unlink': True,

        }
        for ir_model in env['ir.model'].search([])
    ])


