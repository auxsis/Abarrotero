from odoo import api, fields, models, _
from odoo.addons.stock_account.models.product import ProductProduct as ProductProductBase

class Product_Product(ProductProductBase):
    """
    Use: Override base _fifo_vacuum(), facing issue of create account entry with zero amount.
    Added by: Arjun Bhoot @Emipro Technologies
    Date: July-24-2018
    """

    def _get_fifo_candidates_in_move(self):
        """ Find IN moves that can be used to value OUT moves.
        """
        self.ensure_one()
        domain = [('product_id', '=', self.id), ('remaining_qty', '>', 0.0)] + self.env['stock.move']._get_in_base_domain()
        # Override base method.
        # Issue: it's returning all incoming moves without any perticular stock location.
        # Solution: We pass "location_dest_id_ept" from _run_fifo() in context which
        #           contained out move's location_id, so we just added one more domain
        #           for incoming move's location_dest_id.
        # Modification by: Arjun Bhoot @Emipro Technologies
        # Modification date: Oct-17th-2018
        if self._context.get('location_dest_id_ept',''):
            domain = domain + [('location_dest_id','=',self._context.get('location_dest_id_ept'))]
        # Modification over.
        candidates = self.env['stock.move'].search(domain, order='date, id')
        return candidates

    ProductProductBase._get_fifo_candidates_in_move = _get_fifo_candidates_in_move