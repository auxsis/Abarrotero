# -*- coding: utf-8 -*-
from odoo.tools import pycompat
import logging
from odoo.exceptions import AccessError
from odoo import api, fields, models, tools, SUPERUSER_ID, _
_logger = logging.getLogger(__name__)


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        if self._uid in [SUPERUSER_ID]:
            return True
        assert isinstance(model, pycompat.string_types), 'Not a model name: %s' % (model,)
        assert mode in ('read', 'write', 'create', 'unlink'), 'Invalid access mode'
        user = self.env['res.users'].sudo().browse(self._uid)
        # TransientModel records have no access rights, only an implicit access rule
        if model not in self.env:
            _logger.error('Missing model %s', model)
        elif self.env[model].is_transient():
            return True
        # We check if a specific rule exists
        self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END) FROM ir_model_access a
                              JOIN ir_model m ON (m.id = a.model_id) JOIN res_groups_users_rel gu ON (gu.gid = a.group_id)
                             WHERE m.model = %s AND gu.uid = %s AND a.active IS TRUE""".format(mode=mode), (model, self._uid,))
        r = self._cr.fetchone()[0]
        if not r:
            # there is no specific rule. We check the generic rule
            self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END) FROM ir_model_access a JOIN ir_model m ON (m.id = a.model_id)
                                 WHERE a.group_id IS NULL AND m.model = %s AND a.active IS TRUE""".format(mode=mode), (model,))
            r = self._cr.fetchone()[0]
        if model in ['product.product', 'product.template', 'res.partner'] and mode == 'create':
            restrict = user.has_group('user_restriction.group_user_restriction1')
            if restrict:
                r = 0
        if not r and raise_exception:
            groups = '\n\t'.join('- %s' % g for g in self.group_names_with_access(model, mode))
            msg_heads = {
                # Messages are declared in extenso so they are properly exported in translation terms
                'read': _("Sorry, you are not allowed to access this document."),
                'write':  _("Sorry, you are not allowed to modify this document."),
                'create': _("Sorry, you are not allowed to create this kind of document."),
                'unlink': _("Sorry, you are not allowed to delete this document."),
            }
            if groups:
                msg_tail = _("Only users with the following access level are currently allowed to do that") + ":\n%s\n\n(" + _("Document model") + ": %s)"
                msg_params = (groups, model)
            else:
                msg_tail = _("Please contact your system administrator if you think this is an error.") + "\n\n(" + _("Document model") + ": %s)"
                msg_params = (model,)
            _logger.info('Access Denied by ACLs for operation: %s, uid: %s, model: %s', mode, self._uid, model)
            msg = '%s %s' % (msg_heads[mode], msg_tail)
            if model in ['product.product', 'product.template', 'res.partner'] and mode == 'create' and restrict:
                raise AccessError(_('You Have Insufficient Access'))
            raise AccessError(msg % msg_params)
        return bool(r)
