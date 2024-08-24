# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ClsCostCenters(models.Model):
    _name = 'ab_costcenter'
    _description = 'Abdin Cost Centers'

    name = fields.Char(required=True, index=True)
    costcenter_type = fields.Integer()
    tel_no = fields.Char()
    branch_id = fields.Integer()
    hr_name = fields.Char()
    bc_id = fields.Integer()
    code = fields.Char(size=16, required=True, index=True)
    official_name = fields.Char()
    special_id = fields.Char()
    active = fields.Boolean(default=True)
    costcenter_space_sep = fields.Char(search='_search_costcenter_space_sep', compute='_compute_costcenter_space_sep', )

    def _compute_costcenter_space_sep(self):
        for rec in self:
            rec.costcenter_space_sep = rec.id

    def _search_costcenter_space_sep(self, operator, value):
        if operator in ['in', 'ilike', 'not in', 'not ilike']:
            value = [v.strip() for v in value.split()]
            operator = 'in' if operator in ['in', 'ilike'] else 'not in'

        ids = self.sudo().search([('code', operator, value)]).ids
        return [('id', 'in', ids)]

    @api.constrains('code')
    def constrains_ab_costcenter(self):
        for rec in self:
            if ' ' in rec.code:
                raise ValidationError(_("Code must not have spaces"))
            if not rec.bc_id:
                if not (rec.code.startswith('0-') or rec.code.startswith('1-')):
                    raise ValidationError(_("Code must starts with 0- or 1-"))

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        code_args = args + [('code', '=', name), ]

        ids = self._search(code_args, limit=limit, access_rights_uid=name_get_uid)
        if not ids:
            args += [('name', operator, name), ]
            ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return ids

    _sql_constraints = [
        ('ab_costcenter_code_unique', 'unique(code)', 'CODE CAN NOT BE DUPLICATED.'),
    ]

    def write(self, vals):
        res = super(ClsCostCenters, self).write(vals)
        return res
