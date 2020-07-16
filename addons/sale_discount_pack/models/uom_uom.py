from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.osv import osv
from odoo.addons import decimal_precision as dp
from odoo.http import request
import json

class uom_uom(models.Model):
    _inherit = 'uom.uom'

    @api.model
    def get_bigger_unit(self,id,uom_type): 

        query = "select id, name, uom_type, category_id from uom_uom where id = "+str(id)
        request.cr.execute(query)
        uom = request.cr.dictfetchone()
        
        #with open('/odoo_mx_sat/custom/addons/sale_discount_pack/data.json', 'w') as outfile:
        #    json.dump(query, outfile)

        if(uom_type=="bigger"):
            query = "select id, name, uom_type from uom_uom where active = True and uom_type='reference' and category_id = "+str(uom['category_id'])
        if(uom_type=="reference"):
            query = "select id, name, uom_type from uom_uom where active = True and uom_type='bigger' and category_id = "+str(uom['category_id'])
        request.cr.execute(query)
        uom = request.cr.dictfetchone()

        return uom
  