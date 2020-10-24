from odoo import api, fields, models


class ProductTemplate(models.Model):
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

    @api.depends('units_pack', 'list_price')
    def get_price_unit(self):
        for record in self:
            if record.units_pack > 0:
                record.price_unit = record.list_price / record.units_pack
            else:
                record.price_unit = 0
