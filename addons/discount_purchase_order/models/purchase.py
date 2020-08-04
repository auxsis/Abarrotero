# -*- coding: utf-8 -*-
##########################################################################
#
#	Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    monto_desc_maniobra = fields.Float(string="Monto Descuento por Maniobra", compute="_amount_all", store=True)
    monto_desc_flete = fields.Float(string="Monto Descuento por Flete", compute="_amount_all", store=True)
    monto_desc_planes = fields.Float(string="Monto Descuento por Planes", compute="_amount_all", store=True)

    tipo_desc_extra = fields.Selection([('maniobra', 'Maniobra'), ('flete', 'Flete'), ('planes', 'Planes')],
                                       string="Descuento (Maniobra, Flete, Planes)")

    has_desc_extra_maniobra = fields.Boolean(string="Tiene impuesto extra maniobra", default=False)
    has_desc_extra_flete = fields.Boolean(string="Tiene impuesto extra flete", default=False)
    has_desc_extra_planes = fields.Boolean(string="Tiene impuesto extra planes", default=False)

    tipo_calculo_desc_extra = fields.Selection([('percent', 'Porcentaje'), ('fixed', 'Ajuste')],
                                               string="Tipo de Calculo de Descuento (Maniobra, Flete, Planes)")
    tipo_calculo_desc_maniobra = fields.Selection([('percent', 'Porcentaje'), ('fixed', 'Ajuste')],
                                                  string="Tipo de Calculo de Descuento (Maniobra, Flete, Planes)")
    tipo_calculo_desc_flete = fields.Selection([('percent', 'Porcentaje'), ('fixed', 'Ajuste')],
                                               string="Tipo de Calculo de Descuento (Maniobra, Flete, Planes)")
    tipo_calculo_desc_planes = fields.Selection([('percent', 'Porcentaje'), ('fixed', 'Ajuste')],
                                                string="Tipo de Calculo de Descuento (Maniobra, Flete, Planes)")

    cant_desc_extra = fields.Float(string="Cantidad Descuento (Maniobra, Flete, Planes)")
    cant_desc_extra_flete = fields.Float(string="Cantidad Descuento (Flete)")
    cant_desc_extra_planes = fields.Float(string="Cantidad Descuento (Planes)")
    cant_desc_extra_maniobra = fields.Float(string="Cantidad Descuento (Maniobra)")

    total_desc = fields.Float(string="Total Descuento por líneas de productos", compute="_compute_total_desc")

    total_discount = fields.Monetary(string='Total Discount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    global_discount_type = fields.Selection([
        ('fixed', 'Ajuste'),
        ('percent', 'Porcentaje')
    ], string="Tipo de Descuento", )
    global_order_discount = fields.Float(string='Global Discount', store=True, track_visibility='always')

    @api.depends('order_line.subtotal_desc')
    def _compute_total_desc(self):
        for order in self:
            order.total_desc = sum(order.order_line.mapped('subtotal_desc'))

    @api.model
    def _wk_discount_po_settings(self):
        configModel = self.env['res.config.settings']
        vals = {
            'group_discount_purchase_line': 1,
            'group_order_global_discount_po': True,
            'global_discount_tax_po': 'untax',
        }
        defaultSetObj = configModel.create(vals)
        defaultSetObj.execute()
        return True

    @api.depends('order_line.price_total')
    def _amount_all(self):
        # super(PurchaseOrder, self)._amount_all()
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
        if self.has_desc_extra_maniobra:
            if self.tipo_calculo_desc_maniobra == 'percent':
                monto_desc_maniobra = total_amount * (self.cant_desc_extra_maniobra or 0.0) / 100
            elif self.tipo_calculo_desc_maniobra == 'fixed':
                monto_desc_maniobra = self.cant_desc_extra_maniobra

        # Calcula descuentos por Flete
        monto_desc_flete = self.monto_desc_flete or 0.0
        if self.has_desc_extra_flete:
            if self.tipo_calculo_desc_flete == 'percent':
                monto_desc_flete = total_amount * (self.cant_desc_extra_flete or 0.0) / 100
            elif self.tipo_calculo_desc_flete == 'fixed':
                monto_desc_flete = self.cant_desc_extra_flete

        # Calcula descuentos por Planes
        monto_desc_planes = self.monto_desc_planes or 0.0
        if self.has_desc_extra_planes:
            if self.tipo_calculo_desc_planes == 'percent':
                monto_desc_planes = total_amount * (self.cant_desc_extra_planes or 0.0) / 100
            elif self.tipo_calculo_desc_planes == 'fixed':
                monto_desc_planes = self.cant_desc_extra_planes
        return monto_desc_maniobra, monto_desc_flete, monto_desc_planes

    @api.multi
    def force_amount_all(self):
        """Used by discount extra"""
        if self.tipo_desc_extra == 'maniobra':
            self.has_desc_extra_maniobra = True
            self.tipo_calculo_desc_maniobra = self.tipo_calculo_desc_extra
            self.cant_desc_extra_maniobra = self.cant_desc_extra
        elif self.tipo_desc_extra == 'planes':
            self.has_desc_extra_planes = True
            self.tipo_calculo_desc_planes = self.tipo_calculo_desc_extra
            self.cant_desc_extra_planes = self.cant_desc_extra
        elif self.tipo_desc_extra == 'flete':
            self.has_desc_extra_flete = True
            self.tipo_calculo_desc_flete = self.tipo_calculo_desc_extra
            self.cant_desc_extra_flete = self.cant_desc_extra
        self._amount_all()

    @api.multi
    def reset_descuento_maniobra(self):
        self.tipo_calculo_desc_extra = 'fixed'
        self.cant_desc_extra = 0.0
        self.cant_desc_extra_maniobra = 0.0
        self._amount_all()
        self.has_desc_extra_maniobra = False

    @api.multi
    def reset_descuento_flete(self):
        self.tipo_calculo_desc_extra = 'fixed'
        self.cant_desc_extra = 0.0
        self.cant_desc_extra_flete = 0.0
        self._amount_all()
        self.has_desc_extra_flete = False

    @api.multi
    def reset_descuento_planes(self):
        self.tipo_calculo_desc_extra = 'fixed'
        self.cant_desc_extra = 0.0
        self.cant_desc_extra_planes = 0.0
        self._amount_all()
        self.has_desc_extra_planes = False


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    desc1 = fields.Float(string="Desc1(%)")
    desc2 = fields.Float(string="Desc2(%)")
    subtotal_desc = fields.Float(string="Sub-Total Descuentos", compute="_compute_amount")
    price_reduce = fields.Float(compute='_compute_amount', string='Reduccion de Precio', readonly=True, store=True,
                                digits=(12, 4))
    line_sub_total = fields.Monetary(compute='_compute_amount', string='Subtotal de Linea', store=True)
    discount = fields.Float(string='Descuento', digits=dp.get_precision('Discount'), default=0.0)
    discount_type = fields.Selection([
        ('fixed', 'Ajuste'),
        ('percent', 'Porcentaje')
    ], string="Tipo de Descuento", )

    @api.depends('product_qty', 'qty_received', 'price_unit', 'taxes_id', 'desc1', 'desc2')
    def _compute_amount(self):
        for line in self:
            desc1 = 1 - (line.desc1 or 0.0) / 100.0
            desc2 = 1 - (line.desc2 or 0.0) / 100.0
            price = line.price_unit * desc1 * desc2

            if line.qty_received > 0 and line.order_id.state in ('done', 'purchase'):
                quantity = line.qty_received
            else:
                quantity = line.product_qty
            price_reduce = line.price_unit * (1.0 - line.desc1 / 100.0) * (1.0 - line.desc2 / 100.0)
            line_sub_total = quantity * line.price_unit
            taxes = line.taxes_id.compute_all(
                price, line.order_id.currency_id, quantity, product=line.product_id, partner=line.order_id.partner_id)

            line.price_reduce = price_reduce
            line.line_sub_total = line_sub_total
            line.price_tax = taxes['total_included'] - taxes['total_excluded']
            line.price_total = taxes['total_included']
            line.price_subtotal = taxes['total_excluded']
            line.subtotal_desc = (line.price_unit * quantity) - taxes['total_excluded']
