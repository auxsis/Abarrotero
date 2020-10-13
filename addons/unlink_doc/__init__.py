# -*- coding: utf-8 -*-
# unlink_doc
from odoo import SUPERUSER_ID, api


def __unset_model_unlink_perm(env, model: str):
    # Unset unlink permissions on model
    for model_access in env['ir.model.access'].search([
        ('perm_unlink', '=', True), ('model_id.model', '=', model)
    ]):
        if model_access.perm_unlink:
            model_access.perm_unlink = False


def __add_model_unlink_perm(env, group, model: str):
    # Get group named ...
    unlink_res_group = __get_group_by_name(env, group)

    # Add unlink permissions on model for security group "Suprimir/Eliminar Documentos"
    env['ir.model.access'].create([
        {
            'name': f'{model}.perm_unlink', 'model_id': ir_model.id,
            'group_id': unlink_res_group.id,
            'perm_read': False, 'perm_write': False, 'perm_create': False, 'perm_unlink': True,

        }
        for ir_model in env['ir.model'].search([('model', '=', model)])
    ])


def __get_group_by_name(env, name: str):
    # Get group named ...
    return env['res.groups'].search([
        ('name', '=', name),
    ]).ensure_one()


def post_init_hook(cr, registry):
    # Get Environment
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Documents and models
    doc_dict = {
        'Eliminar Líneas de Facturas': 'account.invoice.line',
        'Eliminar Líneas de Compras': 'purchase.order.line',
        'Eliminar Líneas de Ventas': 'sale.order.line',
        'Suprimir Facturas': 'account.invoice',
        'Suprimir Compras': 'purchase.order',
        'Suprimir Ventas': 'sale.order',
    }

    for group, model in doc_dict.items():
        # Unset unlink permissions for ...
        __unset_model_unlink_perm(env, model)

        # Add unlink permissions on all models for security group ...
        __add_model_unlink_perm(env, group, model)
