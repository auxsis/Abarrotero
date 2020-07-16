# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
import json
from odoo.tools import date_utils

_logger = logging.getLogger("__________________________________________" + __name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

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
        order_line = self.order_line.filtered(lambda line: line.taxes_id != False)
        for tax_id in self.mapped('order_line.taxes_id'):
            taxes_vals.append({
                'name': tax_id.name,
                'currency': self.currency_id.symbol,
                'digits': [69, self.currency_id.decimal_places],
                'amount_tax': sum([self.currency_id.round(l.price_tax) for l in self.order_line.filtered(lambda t: t.taxes_id.id == tax_id.id)])
            })

        return taxes_vals

    taxes_widget = fields.Text(compute="_compute_taxes_widget", string="Impuestos")
    total_desc = fields.Float(string="Total Descuento por líneas de productos", compute="_compute_total_desc")

    monto_desc_maniobra = fields.Float(string="Monto Descuento por Maniobra", compute="_amount_all", store=True)
    monto_desc_flete = fields.Float(string="Monto Descuento por Flete", compute="_amount_all", store=True)
    monto_desc_planes = fields.Float(string="Monto Descuento por Planes", compute="_amount_all", store=True)

    tipo_desc_extra = fields.Selection([('maniobra', 'Maniobra'), ('flete', 'Flete'), ('planes', 'Planes')],
                                       string="Descuento (Maniobra, Flete, Planes)")
    tipo_calculo_desc_extra = fields.Selection([('percent', 'Porcentaje'), ('fixed', 'Ajuste')],
                                               string="Tipo de Calculo de Descuento (Maniobra, Flete, Planes)")
    cant_desc_extra = fields.Float(string="Cantidad Descuento (Maniobra, Flete, Planes)")

    @api.depends('order_line.subtotal_desc')
    def _compute_total_desc(self):
        for order in self:
            order.total_desc = sum(order.order_line.mapped('subtotal_desc'))

    @api.depends('order_line.price_total', 'global_order_discount', 'global_discount_type')
    def _amount_all(self):
        super(PurchaseOrder, self)._amount_all()
        for order in self:
            amount_untaxed = amount_tax = 0.0
            total_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                if line.discount_type == 'fixed':
                    total_discount += line.discount
                if line.discount_type == 'percent':
                    total_discount += line.product_qty * (line.price_unit - line.price_reduce)

                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    quantity = 1.0
                    if line.discount_type == 'fixed':
                        price = line.price_unit * line.product_qty - (line.discount or 0.0)
                    else:
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        quantity = line.product_qty
                    taxes = line.taxes_id.compute_all(
                        price, line.order_id.currency_id, quantity, product=line.product_id,
                        partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax

            IrConfigPrmtrSudo = self.env['ir.config_parameter'].sudo()
            discTax = IrConfigPrmtrSudo.get_param('purchase.global_discount_tax_po')

            if discTax == 'untax':
                total_amount = amount_untaxed
            else:
                total_amount = amount_untaxed + amount_tax

            # Aplica descuentos por Maniobra, Flete y Planes
            monto_desc_maniobra, monto_desc_flete, monto_desc_planes = order.add_descuento_amount(total_amount)
            total_amount -= (monto_desc_maniobra + monto_desc_flete + monto_desc_planes)

            if order.global_discount_type == 'percent':
                beforeGlobal = total_amount
                total_amount = total_amount * (1 - (order.global_order_discount or 0.0) / 100)
                total_discount += beforeGlobal - total_amount
            else:
                total_amount = total_amount - (order.global_order_discount or 0.0)
                total_discount = order.global_order_discount

            if discTax == 'untax':
                total_amount = total_amount + amount_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': total_amount,
                'monto_desc_maniobra': monto_desc_maniobra,
                'monto_desc_flete': monto_desc_flete,
                'monto_desc_planes': monto_desc_planes,
                'total_discount': total_discount + monto_desc_maniobra + monto_desc_flete + monto_desc_planes,
            })

    @api.multi
    def add_descuento_amount(self, total_amount):

        # Calcula descuentos por Maniobra
        monto_desc_maniobra = self.monto_desc_maniobra or 0.0
        if self.tipo_desc_extra == 'maniobra':
            if self.tipo_calculo_desc_extra == 'percent':
                monto_desc_maniobra = total_amount * (self.cant_desc_extra or 0.0) / 100
            elif self.tipo_calculo_desc_extra == 'fixed':
                monto_desc_maniobra = self.cant_desc_extra

        # Calcula descuentos por Flete
        monto_desc_flete = self.monto_desc_flete or 0.0
        if self.tipo_desc_extra == 'flete':
            if self.tipo_calculo_desc_extra == 'percent':
                monto_desc_flete = total_amount * (self.cant_desc_extra or 0.0) / 100
            elif self.tipo_calculo_desc_extra == 'fixed':
                monto_desc_flete = self.cant_desc_extra

        # Calcula descuentos por Planes
        monto_desc_planes = self.monto_desc_planes or 0.0
        if self.tipo_desc_extra == 'planes':
            if self.tipo_calculo_desc_extra == 'percent':
                monto_desc_planes = total_amount * (self.cant_desc_extra or 0.0) / 100
            elif self.tipo_calculo_desc_extra == 'fixed':
                monto_desc_planes = self.cant_desc_extra

        return monto_desc_maniobra, monto_desc_flete, monto_desc_planes

    @api.multi
    def force_amount_all(self):
        """Used by discount extra"""
        self._amount_all()

    @api.multi
    def reset_descuento_maniobra(self):
        self.tipo_desc_extra = 'maniobra'
        self.tipo_calculo_desc_extra = 'fixed'
        self.cant_desc_extra = 0.0
        self._amount_all()

    @api.multi
    def reset_descuento_flete(self):
        self.tipo_desc_extra = 'flete'
        self.tipo_calculo_desc_extra = 'fixed'
        self.cant_desc_extra = 0.0
        self._amount_all()

    @api.multi
    def reset_descuento_planes(self):
        self.tipo_desc_extra = 'planes'
        self.tipo_calculo_desc_extra = 'fixed'
        self.cant_desc_extra = 0.0
        self._amount_all()

    @api.multi
    def _add_supplier_to_product(self):
        for line in self.order_line:
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            seller_id = line.product_id.seller_ids.filtered(lambda r: r.name == partner)
            if seller_id:
                seller_id.price = line.price_unit
            else:
                super(PurchaseOrder, self)._add_supplier_to_product()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_id')
    def _compute_line(self):
        linea = 0
        for line in self:
            linea += 1
            line.number_line = 1
            
    number_line = fields.Integer(string="Linea", compute="_compute_line", store=True)
    desc1 = fields.Float(string="Desc1(%)")
    desc2 = fields.Float(string="Desc2(%)")
    subtotal_desc = fields.Float(string="Sub-Total Descuentos", compute="_compute_amount")
    stock_disponible = fields.Float(string="Stock disponible", related="product_id.qty_available", store=True)
    coste_neto = fields.Float(string="Coste Neto", compute="_compute_amount")

    @api.depends('price_unit', 'discount_type', 'discount', 'taxes_id', 'qty_received')
    def _get_price_reduce(self):
        super(PurchaseOrderLine, self)._get_price_reduce()
        for line in self:
            if line.qty_received > 0:
                if line.discount_type == 'fixed' and line.qty_received:
                    price_reduce = line.price_unit * line.qty_received - line.discount
                    line.price_reduce = price_reduce/line.qty_received
                else:
                    line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                price = line.price_unit
                quantity = line.qty_received
                taxes = line.taxes_id.compute_all(
                    price, line.order_id.currency_id, quantity, product=line.product_id, partner=line.order_id.partner_id)
                line.line_sub_total = quantity * line.price_unit
                line.price_subtotal = taxes['total_excluded']

    @api.depends('qty_received', 'price_unit', 'taxes_id', 'discount', 'discount_type', 'desc1', 'desc2')
    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()
        for line in self:

            desc1 = 1 - (line.desc1 or 0.0) / 100.0
            desc2 = 1 - (line.desc2 or 0.0) / 100.0
            price = line.price_unit * desc1 * desc2

            if line.qty_received > 0:
                quantity = line.qty_received
            else:
                quantity = line.product_qty
            taxes = line.taxes_id.compute_all(
                price, line.order_id.currency_id, quantity, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'subtotal_desc': (line.price_unit * quantity) - taxes['total_excluded'],
                'coste_neto': (taxes['total_included'] / quantity) if quantity else 0,
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

