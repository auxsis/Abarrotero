# -*- coding: utf-8 -*-
# independent_product_profit_margin
from odoo import SUPERUSER_ID, api
from . import models

prod_templ_dct = dict()


def pre_init_hook(cr):
    global prod_templ_dct
    _prod_templ_dct = prod_templ_dct
    env = api.Environment(cr, SUPERUSER_ID, {})

    for prod_templ in env['product.template'].search([
        '|', ('profit_margin', '>', 0), ('profit_margin2', '>', 0)
    ]):
        _prod_templ_dct[prod_templ.id] = {
            'profit_margin': prod_templ.profit_margin,
            'profit_margin2': prod_templ.profit_margin2,
        }


def post_init_hook(cr, registry):
    global prod_templ_dct
    _prod_templ_dct = prod_templ_dct
    env = api.Environment(cr, SUPERUSER_ID, {})

    for prod_templ in env['product.template'].browse([
        key for key in _prod_templ_dct
    ]):
        prod_templ.write({
            'profit_margin': _prod_templ_dct[prod_templ.id]['profit_margin'],
            'profit_margin2': _prod_templ_dct[prod_templ.id]['profit_margin2'],
        })

    del prod_templ_dct
    prod_templ_dct = dict()
