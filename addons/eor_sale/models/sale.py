# -*- coding: utf-8 -*-

import json
import logging

from odoo import _, api, fields, models
from odoo.tools import date_utils
from odoo.osv import expression

_logger = logging.getLogger('-----------------------------------------------------------------------' + __name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('ingressed', 'Ingressed'),
        ('delivered', 'Delivered')])

    @api.depends('state', 'order_line.invoice_status', 'order_line.invoice_lines',
                 'order_line.is_delivery', 'order_line.is_downpayment', 'order_line.product_id.invoice_policy')
    def _get_invoiced(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.

        The invoice_ids are obtained thanks to the invoice lines of the SO lines, and we also search
        for possible refunds created directly from existing invoices. This is necessary since such a
        refund is not directly linked to the SO.
        """
        # Ignore the status of the deposit product
        deposit_product_id = self.env['sale.advance.payment.inv']._default_product_id()
        line_invoice_status_all = [(d['order_id'][0], d['invoice_status']) for d in
                                   self.env['sale.order.line'].read_group(
                                       [('order_id', 'in', self.ids), ('product_id', '!=', deposit_product_id.id)],
                                       ['order_id', 'invoice_status'], ['order_id', 'invoice_status'], lazy=False)]
        for order in self:
            invoice_ids = order.order_line.mapped('invoice_lines').mapped('invoice_id').filtered(
                lambda r: r.type in ['out_invoice', 'out_refund'])
            # Search for invoices which have been 'cancelled' (filter_refund = 'modify' in
            # 'account.invoice.refund')
            # use like as origin may contains multiple references (e.g. 'SO01, SO02')
            refunds = invoice_ids.search([('origin', 'like', order.name), ('company_id', '=', order.company_id.id),
                                          ('type', 'in', ('out_invoice', 'out_refund'))])
            invoice_ids |= refunds.filtered(lambda r: order.name in [origin.strip() for origin in r.origin.split(',')])

            # Search for refunds as well
            domain_inv = expression.OR([
                ['&', ('origin', '=', inv.number), ('journal_id', '=', inv.journal_id.id)]
                for inv in invoice_ids if inv.number
            ])
            if domain_inv:
                refund_ids = self.env['account.invoice'].search(expression.AND([
                    ['&', ('type', '=', 'out_refund'), ('origin', '!=', False)],
                    domain_inv
                ]))
            else:
                refund_ids = self.env['account.invoice'].browse()

            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]

            if order.state not in ('sale', 'done', 'delivered'):
                invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                invoice_status = 'to invoice'
            elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                invoice_status = 'invoiced'
            elif line_invoice_status and all(
                            invoice_status in ['invoiced', 'upselling'] for invoice_status in line_invoice_status):
                invoice_status = 'upselling'
            else:
                invoice_status = 'no'

            order.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
                'invoice_status': invoice_status
            })

        for order in self:
            order_line = order.order_line.filtered(
                lambda x: not x.is_delivery and not x.is_downpayment and not x.display_type)
            if all(line.product_id.invoice_policy == 'delivery' and line.invoice_status == 'no' for line in
                   order_line):
                order.update({'invoice_status': 'no'})

    @api.depends('order_line.tax_id', 'amount_tax')
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
        order_line = self.order_line.filtered(lambda line: line.tax_id != False)
        for tax_id in self.mapped('order_line.tax_id'):
            taxes_vals.append({
                'name': tax_id.name,
                'currency': self.currency_id.symbol,
                'digits': [69, self.currency_id.decimal_places],
                'amount_tax': sum([self.currency_id.round(l.price_tax) for l in
                                   self.order_line.filtered(lambda t: t.tax_id.id == tax_id.id)])
            })

        return taxes_vals

    taxes_widget = fields.Text(compute="_compute_taxes_widget", string="Impuestos")
    x_obervaciones = fields.Text('Observaciones')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['sale', 'done', 'delivered']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('price_unit', 'price_tax')
    def _compute_price(self):
        for line in self:
            price_unit = line.price_unit
            # Taxes without discount
            taxes = line.tax_id.compute_all(price_unit, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            price_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            if line.product_uom_qty > 0:
                price_tax = price_tax / line.product_uom_qty

            if line.price_unit_tax <= 0:
                line.price_unit_tax = price_unit + price_tax
            if line.product_id.units_pack > 0:
                line.precio_x_pieza = line.price_unit_tax / line.product_id.units_pack

    @api.depends('product_id')
    def _compute_stock_available(self):
        for line in self:
            line.stock_disponible = line.product_id.qty_available

    stock_disponible = fields.Float(string="Stock disponible", compute="_compute_stock_available")
    precio_x_pieza = fields.Monetary(string='Precio por pieza', compute='_compute_price')
    price_unit_tax = fields.Float(default=_compute_price, string="Precio Neto",store=True)#change to default 1.0
    pricelist_id = fields.Many2one('product.pricelist', string='Lista de Precio')

    # override 1.1
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','price_unit_tax')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit_tax * (1 - (line.discount or 0.0) / 100.0)#change to price_unit_tax
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _compute_editar(self):
        for record in self:
            record['x_studio_authorization1'] = False
            if self.env.user.has_group('<UserAccessGroup>'):
                record['x_studio_authorization1'] = True


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_cancel(self):
        self.mapped('move_lines')._action_cancel()
        self.write({'is_locked': True})
        self.compute_state_sale_order()
        return True

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        self.compute_state_sale_order()
        return res

    @api.multi
    def compute_state_sale_order(self):
        sale = self.sale_id
        if sale:
            in_done = False
            pickings = self.sale_id.picking_ids
            for picking in pickings:
                if picking.state in ['done']:
                    in_done = True
                elif picking.state not in ['done', 'cancel']:
                    in_done = False
                    break
            if in_done:
                sale.write({'state': 'delivered'})
            else:
                sale.write({'state': 'sale'})
