# -*- coding: utf-8 -*-

from lxml import etree

from odoo import models, api
from odoo.osv.orm import setup_modifiers


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                          submenu=submenu)
        user = self.env.user

        if view_type == 'tree' and not all(
            user.has_group(group_ext_id)
            for group_ext_id in (
                'invoice_doc_type_ir_rules.group_remisiones',
                'invoice_doc_type_ir_rules.group_cfdi',
                'invoice_doc_type_ir_rules.group_vacios',
                'invoice_doc_type_ir_rules.group_vacios',
            )
        ):
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//tree/field[@name='x_document_type']")
            for node in nodes:
                node.set('invisible', '1')
                setup_modifiers(node, in_tree_view=True)
            res['arch'] = etree.tostring(doc)

        return res
