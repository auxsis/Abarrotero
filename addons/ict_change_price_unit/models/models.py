# -*- coding: utf-8 -*-

from odoo import models, api


class ICTChangePriceUnit(models.Model):
    _inherit = "inter.company.transfer.line.ept"

    @api.depends('product_id', 'inter_transfer_id')
    def default_price_get(self):
        """
        Get the Product Unit Price
        """
        for record in self:
            if record.product_id and record.inter_transfer_id.state:
                # Always get the product data (price) from root company (Grupo Abarrotero Guerrerense)
                if record.inter_transfer_id.state in 'draft':
                    product_id = record.with_context(
                        # id = 16 -> name='Almacén Nuevo Severo'
                        # id = 1  -> name='Grupo Abarrotero Guerrerense'
                        force_company=16 if self.env.user.company_id.id == 16 else 1
                    ).product_id

                    record.price = product_id.base_imponible_costo
                    record.net_price = product_id.standard_price
            else:
                record.price = record.net_price = 0.0
