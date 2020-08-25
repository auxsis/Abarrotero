# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
import json
import itertools
from odoo.tools import date_utils, DEFAULT_SERVER_DATETIME_FORMAT, OrderedSet
from collections import defaultdict, MutableMapping, OrderedDict
from odoo.exceptions import Warning
_logger = logging.getLogger("__________________________________________" + __name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    observations = fields.Text(string="Observaciones")
    x_document_type = fields.Selection([('cfdi','CFDI'),('remision','Remision')], 'Tipo de Documento')

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

    @api.multi
    def action_rfq_send(self):
        res = super(PurchaseOrder, self).action_rfq_send()
        res['context']['custom_layout'] = 'eor_purchase.mail_notification_paynow'
        return res

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

    def _update_cache(self, values, validate=True):
        """ Update the cache of ``self`` with ``values``.

            :param values: dict of field values, in any format.
            :param validate: whether values must be checked
        """
        def is_monetary(pair):
            return pair[0].type == 'monetary'

        self.ensure_one()
        cache = self.env.cache
        fields = self._fields
        try:
            field_values = [(fields[name], value) for name, value in values.items()]
        except KeyError as e:
            raise ValueError("Invalid field %r on model %r" % (e.args[0], self._name))

        # convert monetary fields last in order to ensure proper rounding
        for field, value in sorted(field_values, key=is_monetary):
            cache.set(self, field, field.convert_to_cache(value, self, validate))

            # set inverse fields on new records in the comodel
            if field.relational:
                inv_recs = self[field.name].filtered(lambda r: not r.id)
                if not inv_recs:
                    continue
                for invf in self._field_inverses[field]:
                    # DLE P98: `test_40_new_fields`
                    # /home/dle/src/odoo/master-nochange-fp/odoo/addons/test_new_api/tests/test_new_fields.py
                    # Be careful to not break `test_onchange_taxes_1`, `test_onchange_taxes_2`, `test_onchange_taxes_3`
                    # If you attempt to find a better solution
                    for inv_rec in inv_recs:
                        if not cache.contains(inv_rec, invf):
                            val = invf.convert_to_cache(self, inv_rec, validate=False)
                            cache.set(inv_rec, invf, val)
                        else:
                            invf._update(inv_rec, self)

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        env = self.env
        if isinstance(field_name, list):
            names = field_name
        elif field_name:
            names = [field_name]
        else:
            names = []

        if not all(name in self._fields for name in names):
            return {}

        def PrefixTree(model, dotnames):
            """ Return a prefix tree for sequences of field names. """
            if not dotnames:
                return {}
            # group dotnames by prefix
            suffixes = defaultdict(list)
            for dotname in dotnames:
                # name, *names = dotname.split('.', 1)
                names = dotname.split('.', 1)
                name = names.pop(0)
                suffixes[name].extend(names)
            # fill in prefix tree in fields order
            tree = OrderedDict()
            for name, field in model._fields.items():
                if name in suffixes:
                    tree[name] = subtree = PrefixTree(model[name], suffixes[name])
                    if subtree and field.type == 'one2many':
                        subtree.pop(field.inverse_name, None)
            return tree

        class Snapshot(dict):
            """ A dict with the values of a record, following a prefix tree. """
            __slots__ = ()

            def __init__(self, record, tree):
                # put record in dict to include it when comparing snapshots
                super(Snapshot, self).__init__({'<record>': record, '<tree>': tree})
                for name in tree:
                    self.fetch(name)

            def fetch(self, name):
                """ Set the value of field ``name`` from the record's value. """
                record = self['<record>']
                tree = self['<tree>']
                if record._fields[name].type in ('one2many', 'many2many'):
                    # x2many fields are serialized as a list of line snapshots
                    self[name] = [Snapshot(line, tree[name]) for line in record[name]]
                else:
                    self[name] = record[name]

            def has_changed(self, name):
                """ Return whether a field on record has changed. """
                record = self['<record>']
                subnames = self['<tree>'][name]
                if record._fields[name].type not in ('one2many', 'many2many'):
                    return self[name] != record[name]
                return (
                    len(self[name]) != len(record[name])
                    or (
                        set(line_snapshot["<record>"].id for line_snapshot in self[name])
                        != set(record[name]._ids)
                    )
                    or any(
                        line_snapshot.has_changed(subname)
                        for line_snapshot in self[name]
                        for subname in subnames
                    )
                )

            def diff(self, other):
                """ Return the values in ``self`` that differ from ``other``.
                    Requires record cache invalidation for correct output!
                """
                record = self['<record>']
                result = {}
                for name, subnames in self['<tree>'].items():
                    if (name == 'id') or (other.get(name) == self[name]):
                        continue
                    field = record._fields[name]
                    if field.type not in ('one2many', 'many2many'):
                        result[name] = field.convert_to_onchange(self[name], record, {})
                    else:
                        # x2many fields: serialize value as commands
                        result[name] = commands = [(5,)]
                        for line_snapshot in self[name]:
                            line = line_snapshot['<record>']
                            # line = line._origin or line
                            if not line.id:
                                # new line: send diff from scratch
                                line_diff = line_snapshot.diff({})
                                commands.append((0, line.id.ref or 0, line_diff))
                            else:
                                # existing line: check diff from database
                                # (requires a clean record cache!)
                                line_diff = line_snapshot.diff(Snapshot(line, subnames))
                                if line_diff:
                                    # send all fields because the web client
                                    # might need them to evaluate modifiers
                                    line_diff = line_snapshot.diff({})
                                    commands.append((1, line.id, line_diff))
                                else:
                                    commands.append((4, line.id))
                return result

        nametree = PrefixTree(self.browse(), field_onchange)

        # prefetch x2many lines without data (for the initial snapshot)
        for name, subnames in nametree.items():
            if subnames and values.get(name):
                # retrieve all ids in commands, and read the expected fields
                line_ids = []
                for cmd in values[name]:
                    if cmd[0] in (1, 4):
                        line_ids.append(cmd[1])
                    elif cmd[0] == 6:
                        line_ids.extend(cmd[2])
                lines = self.browse()[name].browse(line_ids)
                lines.read(list(subnames), load='_classic_write')

        # Isolate changed values, to handle inconsistent data sent from the
        # client side: when a form view contains two one2many fields that
        # overlap, the lines that appear in both fields may be sent with
        # different data. Consider, for instance:
        #
        #   foo_ids: [line with value=1, ...]
        #   bar_ids: [line with value=1, ...]
        #
        # If value=2 is set on 'line' in 'bar_ids', the client sends
        #
        #   foo_ids: [line with value=1, ...]
        #   bar_ids: [line with value=2, ...]
        #
        # The idea is to put 'foo_ids' in cache first, so that the snapshot
        # contains value=1 for line in 'foo_ids'. The snapshot is then updated
        # with the value of `bar_ids`, which will contain value=2 on line.
        #
        # The issue also occurs with other fields. For instance, an onchange on
        # a move line has a value for the field 'move_id' that contains the
        # values of the move, among which the one2many that contains the line
        # itself, with old values!
        #
        changed_values = {name: values[name] for name in names}
        # set changed values to null in initial_values; not setting them
        # triggers default_get() on the new record when creating snapshot0
        initial_values = dict(values, **dict.fromkeys(names, False))

        # create a new record with values, and attach ``self`` to it
        with env.do_in_onchange():
            record = self.new(initial_values)
            # attach ``self`` with a different context (for cache consistency)
            record._origin = self.with_context(__onchange=True)

        # make a snapshot based on the initial values of record
        with env.do_in_onchange():
            snapshot0 = snapshot1 = Snapshot(record, nametree)

        # store changed values in cache, and update snapshot0
        with env.do_in_onchange():
            record._update_cache(changed_values, validate=False)
            for name in names:
                snapshot0.fetch(name)

        # determine which field(s) should be triggered an onchange
        todo = list(names or nametree)
        done = set()

        # dummy assignment: trigger invalidations on the record
        with env.do_in_onchange():
            for name in todo:
                if name == 'id':
                    continue
                value = record[name]
                field = self._fields[name]
                if field.type == 'many2one' and field.delegate and not value:
                    # do not nullify all fields of parent record for new records
                    continue
                record[name] = value

        result = {'warnings': OrderedSet()}

        # process names in order
        with env.do_in_onchange():
            while todo:
                # apply field-specific onchange methods
                for name in todo:
                    if field_onchange.get(name):
                        record._onchange_eval(name, field_onchange[name], result)
                    done.add(name)

                # determine which fields to process for the next pass
                todo = [
                    name
                    for name in nametree
                    if name not in done and snapshot0.has_changed(name)
                ]

            # make the snapshot with the final values of record
            snapshot1 = Snapshot(record, nametree)

        # determine values that have changed by comparing snapshots
        self.invalidate_cache()
        result['value'] = snapshot1.diff(snapshot0)

        # format warnings
        warnings = result.pop('warnings')
        if len(warnings) == 1:
            title, message = warnings.pop()
            result['warning'] = dict(title=title, message=message)
        elif len(warnings) > 1:
            # concatenate warning titles and messages
            title = _("Warnings")
            message = "\n\n".join(itertools.chain(*warnings))
            result['warning'] = dict(title=title, message=message)

        return result


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
            # sellers = self.product_id.seller_ids.mapped('id')
            # vendor = self.env['product.supplierinfo'].search([('id', 'in', sellers), ('name', '=', partner.id)])
            # if vendor:
            #     self.price_unit = vendor[0].price
            # else:
            self.price_unit = self.product_id.base_imponible_costo
        else:
            raise Warning("Seleccione un proveedor")

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            if self.product_id.seller_ids.filtered(lambda s: s.name.id == self.partner_id.id):
                self.price_unit = 0.0
            return

        # price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
        #                                                                      self.product_id.supplier_taxes_id,
        #                                                                      self.taxes_id,
        #                                                                      self.company_id) if seller else 0.0
        price_unit = self.env['account.tax']._fix_tax_included_price_company(self.product_id.base_imponible_costo,
                                                                             self.product_id.supplier_taxes_id,
                                                                             self.taxes_id,
                                                                             self.company_id) if seller else 0.0

        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        # self.price_unit = price_unit