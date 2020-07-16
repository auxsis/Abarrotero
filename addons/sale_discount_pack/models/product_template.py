from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.osv import osv


class product_template(models.Model):
    _inherit = 'product.template'

    price_unit = fields.Float(
                                    'Precio por Unidad',
                                    default=1.0,
                                    help="Price at which the product is sold to customers.",
                                    compute='get_price_unit',
                             )
    units_pack = fields.Integer(
                                    'Unidades por Paquete',
                                    default=1,
                                    help="Price at which the product is sold to customers."
                             )
    


    @api.depends('units_pack', 'taxed_lst_price')
    def get_price_unit(self):

        for record in self:
            record.price_unit = record.taxed_lst_price / record.units_pack
