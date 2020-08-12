# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
import json
from odoo.tools import date_utils
from odoo.exceptions import Warning

_logger = logging.getLogger("__________________________________________" + __name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    observations = fields.Text(string="Observaciones")

    @api.depends('order_line.taxes_id', 'amount_tax')
    def _compute_taxes_widget(self):
        for order in self:
            taxes_vals = order._get_taxes_JSON_values()
            if taxes_vals:
                inf = {
                    'title': _('Hola Mundo'),
                    'content': taxes_vals
                }
                order.taxes_widget = json.dumps(inf, default=date_utils.json_default)
            else:
                order.taxes_widget = json.dumps(False)

    def _get_taxes_JSON_values(self):
        taxes_vals = []
        # order_line = self.order_line.filtered(lambda line: line.taxes_id != False)
        for tax_id in self.mapped('order_line.taxes_id'):
            taxes_vals.append({
                'name': tax_id.name,
                'currency': self.currency_id.symbol,
                'digits': [69, self.currency_id.decimal_places],
                'amount_tax': sum([self.currency_id.round(l.price_tax) for l in self.order_line.filtered(lambda t: tax_id.id in t.taxes_id.mapped('id'))])
            })

        return taxes_vals

    taxes_widget = fields.Text(compute="_compute_taxes_widget", string="Impuestos")

    @api.multi
    def _add_supplier_to_product(self):
        for line in self.order_line:
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            seller_id = line.product_id.seller_ids.filtered(lambda r: r.name == partner)
            if seller_id:
                seller_id.price = line.price_unit
            else:
                super(PurchaseOrder, self)._add_supplier_to_product()

    @api.multi
    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        if res:
            if res.get('context') == None:
                res['context'] = {}
            res['context'].update({
                'default_maniobra_discount': self.monto_desc_maniobra,
                'default_flete_discount': self.monto_desc_flete,
                'default_plans_discount': self.monto_desc_planes,
                'ref_only': True,
            })
        return res

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_id')
    def _compute_line(self):
        linea = 0
        for line in self:
            linea += 1
            line.number_line = 1

    number_line = fields.Integer(string="Linea", compute="_compute_line", store=True)
    stock_disponible = fields.Float(string="Stock disponible", related="product_id.qty_available", store=True)
    coste_neto = fields.Float(string="Coste Neto", compute="_compute_amount")

    @api.depends('product_qty', 'qty_received', 'price_unit', 'taxes_id', 'desc1', 'desc2')
    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()
        for line in self:
            taxes2 = line.taxes_id.compute_all(
                line.price_unit, line.order_id.currency_id, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'coste_neto': taxes2['total_included'],
            })

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes_ids = line.product_id.supplier_taxes_id.filtered(
                lambda r: not line.company_id or r.company_id == line.company_id)
            taxes = taxes_ids.filtered(lambda r: r.company_id in [self.env.user.company_id])
            line.taxes_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(PurchaseOrderLine, self).onchange_product_id()
        partner = self.order_id.partner_id
        if partner:
            sellers = self.product_id.seller_ids.mapped('id')
            vendor = self.env['product.supplierinfo'].search([('id', 'in', sellers), ('name', '=', partner.id)])
            if vendor:
                self.price_unit = vendor[0].price
            else:
                self.price_unit = self.product_id.base_imponible_costo
        else:
            raise Warning("Seleccione un proveedor")
