# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from .extra_functions import get_modified_name


class Region(models.Model):
    _name = 'ab_hr_region'
    _description = 'ab_hr_region'
    name = fields.Char(required=True)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        mod_name = get_modified_name(name)
        args += ['|',
                 ('name', operator, name),
                 ('name', operator, mod_name),
                 ]
        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return ids
