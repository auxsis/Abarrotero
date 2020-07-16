from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.osv import osv
from odoo.addons import decimal_precision as dp
import json , sys

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'  
      
    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        try:
            unit_type = self.product_uom.uom_type             

            if(str(unit_type)==str("bigger")):
                #if(int(self.product_uom_qty) > int(self.product_id.units_discount)):                    
                price = self.product_id.best_price * (1 - (self.discount or 0.0) / 100.0)
                self.price_unit = price
                if not (self.product_id and self.product_uom and

                        self.order_id.partner_id and self.order_id.pricelist_id and

                        self.order_id.pricelist_id.discount_policy == 'without_discount' and

                        self.env.user.has_group('sale.group_discount_per_so_line')):
                    return
                    
        except Exception as e:
            exc_traceback = sys.exc_info()
            raise Warning(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno))
            #with open('/odoo_mx_sat/custom/addons/sale_discount_pack/data.json', 'w') as outfile:
            #   json.dump(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno), outfile)

    #@api.onchange('product_uom_qty')
    #def on_change_product_uom_qty(self):
    #    try:
    #        
    #        self.discount = float(10.5)
    #        line_id = self._origin.id
    #        
    #        order_line = self.env['sale.order.line'].search([('id', '=', line_id)], limit=1) 
    #        
    #        f = open("/odoo_mx_sat/custom/addons/sale_discount_pack/data.json", "a")
    #        f.write(str((self.price_unit)))
    #        f.close()
#
    #        query = "update sale_order_line set price_unit = " + str(self.product_id.pack_price) + " where id = " + str(line_id)
    #        request.cr.execute(query)
#
    #        order_line.price_unit = str(self.product_id.pack_price)
    #        order_line.update{'price_unit':str(self.product_id.pack_price)}
    #        self.price_unit = self.product_id.pack_price
            #uom_object = self.env['uom.uom']
#
            ## current qty
            #qty = self.product_uom_qty
#
            ## current uom selected
            #unit_category = self.product_uom.category_id.id
            #unit_type = self.product_uom.uom_type        
#
            #if(str(unit_type)=="bigger"):            
            #    order_line.price_unit = str(self.product_id.pack_price)
            #    order_line.update{'price_unit':str(self.product_id.pack_price)}
#
#
            #    raise Warning(self.product_id.pack_price)
        except Exception as e:
            exc_traceback = sys.exc_info()
            with open('/odoo_mx_sat/custom/addons/sale_discount_pack/data.json', 'w') as outfile:
               json.dump(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno), outfile)

        #USAR PARA POS
        #if(str(unit_type)=="reference"):
        #    # get bigger uom            
        #    uom_bigger = uom_object.search([('category_id', '=', unit_category),('uom_type', '=', 'bigger')], limit=1)            
        #    if(uom_bigger):
        #        if(str(uom_bigger.uom_type)=="bigger"):  
        #            self.price_unit = self.product_id.pack_price              
        #            #items_per_pack = int(uom_bigger.factor_inv)
        #            #if(int(items_per_pack)>0):
        #            #    if(int(qty) >= int(items_per_pack)):
        #            #        raise Warning("Apply")
