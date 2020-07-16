from odoo import api, fields, models, _
from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase
from odoo.addons.stock_account.models.stock import StockMove as StockAccount_StockMove
import logging

_logger = logging.getLogger(__name__)

class Stock_Move(StockAccount_StockMove):
    """
    Use: Override base _fifo_vacuum(), facing issue of create account entry with zero amount.
    Added by: Arjun Bhoot @Emipro Technologies
    Date: July-24-2018
    """

    @api.model
    def _run_fifo(self, move, quantity=None):
        """ Value `move` according to the FIFO rule, meaning we consume the
        oldest receipt first. Candidates receipts are marked consumed or free
        thanks to their `remaining_qty` and `remaining_value` fields.
        By definition, `move` should be an outgoing stock move.

        :param quantity: quantity to value instead of `move.product_qty`
        :returns: valued amount in absolute
        """
        move.ensure_one()

        # Deal with possible move lines that do not impact the valuation.
        valued_move_lines = move.move_line_ids.filtered(lambda ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
        valued_quantity = 0
        for valued_move_line in valued_move_lines:
            valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)

        # Find back incoming stock moves (called candidates here) to value this move.
        qty_to_take_on_candidates = quantity or valued_quantity
        # Issue: _get_fifo_candidates_in_move() was returning all locations moves with
        #           date and id accending order, it's not returning perticular location move.
        # Modification : While calling _get_fifo_candidates_in_move() we are parsing current
        #               move's location_id as incoming move's location_dest_id, by this solution
        #               only those moves will get back which have same location_dest_id which
        #               current move has location_id.
        # Modification by: Arjun Bhoot @Emipro Technologies
        # Modification date: Oct-17th-2018
        candidates = move.product_id.with_context(location_dest_id_ept=move.location_id.id)._get_fifo_candidates_in_move()
        # Modification over.

        new_standard_price = 0
        tmp_value = 0  # to accumulate the value taken on the candidates
        for candidate in candidates:
            new_standard_price = candidate.price_unit
            if candidate.remaining_qty <= qty_to_take_on_candidates:
                qty_taken_on_candidate = candidate.remaining_qty
            else:
                qty_taken_on_candidate = qty_to_take_on_candidates

            # As applying a landed cost do not update the unit price, naivelly doing
            # something like qty_taken_on_candidate * candidate.price_unit won't make
            # the additional value brought by the landed cost go away.
            candidate_price_unit = candidate.remaining_value / candidate.remaining_qty
            value_taken_on_candidate = qty_taken_on_candidate * candidate_price_unit
            candidate_vals = {
                'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
                'remaining_value': candidate.remaining_value - value_taken_on_candidate,
            }
            candidate.write(candidate_vals)

            qty_to_take_on_candidates -= qty_taken_on_candidate
            tmp_value += value_taken_on_candidate
            if qty_to_take_on_candidates == 0:
                break

        # Update the standard price with the price of the last used candidate, if any.
        if new_standard_price and move.product_id.cost_method == 'fifo':
            move.product_id.sudo().standard_price = new_standard_price

        # If there's still quantity to value but we're out of candidates, we fall in the
        # negative stock use case. We chose to value the out move at the price of the
        # last out and a correction entry will be made once `_fifo_vacuum` is called.
        if qty_to_take_on_candidates == 0:
            move.write({
                'value': -tmp_value if not quantity else move.value or -tmp_value,  # outgoing move are valued negatively
                'price_unit': -tmp_value / move.product_qty,
            })
        elif qty_to_take_on_candidates > 0:
            last_fifo_price = new_standard_price or move.product_id.standard_price
            negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
            tmp_value += abs(negative_stock_value)
            vals = {
                'remaining_qty': move.remaining_qty + -qty_to_take_on_candidates,
                'remaining_value': move.remaining_value + negative_stock_value,
                'value': -tmp_value,
                'price_unit': -1 * last_fifo_price,
            }
            move.write(vals)
        return tmp_value

    StockAccount_StockMove._run_fifo = _run_fifo

class StockMove(models.Model):
    _inherit = "stock.move"

    #update the quants in source and destinition location for a product
    @api.multi
    def stock_quant_update_ept(self):
        context={}
        for move in self:
            if move.state == "done" and move.product_id.type == "product":
                for line in move.move_line_ids:
                    lot = line.lot_id or None
                    package = line.package_id or None
                    owner = line.owner_id or None
                    qty = line.product_uom_id._compute_quantity(line.qty_done, line.product_id.uom_id)
                    self.env['stock.quant']._update_available_quantity(line.product_id, line.location_id, qty,lot,package,owner)
                    self.env['stock.quant']._update_available_quantity(line.product_id, line.location_dest_id, qty * -1,lot,package,owner)
            context.update(self._context)
            context.update({'from_stock_quant_update_ept':True})
            move.with_context(context)._action_cancel()
        return True

    def _action_cancel(self):
        # if any(move.state == 'done' for move in self):
        #     raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
        for move in self:
            if move.state == 'cancel':
                continue
            move._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids and move.move_dest_ids._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
        self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        for move in self:
            account_move = self.env['account.move'].search([('stock_move_id', '=', move.id)])
            if account_move:
                for am in account_move:
                    am.line_ids.sudo().remove_move_reconcile()
                    am.button_cancel()
                    am.unlink()
        return True

    def _do_unreserve(self):
        for move in self:
            for line in move.move_line_ids:#for unlink the stock move line
                line.state = 'draft'
            move.move_line_ids.unlink()
            if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                move.state = 'waiting'
            elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                move.state = 'waiting'
            else:
                move.state = 'confirmed'
        return True