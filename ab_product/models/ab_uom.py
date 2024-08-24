from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AbdinUom(models.Model):
    _name = 'ab_uom'
    _description = 'Abdin Unit Of Measure'
    _order = 'unit_size'

    type_id = fields.Many2one('ab_uom_type', required=True)
    unit_no = fields.Integer(required=True)
    unit_size = fields.Selection(selection=[(
        'large', 'Large'), ('medium', 'Medium'), ('small', 'Small')], required=True)

    @api.constrains('unit_no')
    def validate_unit_of_measure(self):
        for record in self:
            if record.unit_no < 1:
                raise UserError(_("Unit number must be greater than 1."))

            uom_criteria = [('type_id', '=', record.type_id.id),
                            ('unit_size', '=', record.unit_size),
                            ('unit_no', '=', record.unit_no)]
            uom_records = self.sudo().search(uom_criteria)
            if len(uom_records) > 1:
                raise UserError(_("Duplicate unit of measure found."))

    def name_get(self):
        res = []
        for rec in self:
            if self.env.context.get('uom_only_type', False):
                unit_size_selection = {
                    'large': 'L', 'medium': 'M', 'small': 'S'}
                res.append(
                    (rec.id, f"{rec.type_id.name} ({unit_size_selection[rec.unit_size]})"))
            else:
                res.append((rec.id, f"{rec.unit_no} {rec.type_id.name}"))

        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name != '' or operator != 'ilike':
            name_parts = name.split(" ")
            for part in name_parts:
                args += ['|', ('type_id', operator, part),
                         ('unit_no', operator, part)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


class AbdinUomType(models.Model):
    _name = 'ab_uom_type'
    _description = 'Abdin Uom Type'

    name = fields.Char(required=True)

    @api.constrains('name')
    def _constrains_uom_type(self):
        for rec in self:
            uom_type = self.search([('name', '=ilike', rec.name)])
            if len(uom_type) > 1:
                raise UserError(
                    _(f"The Uom name '{rec.name}' must be unique. Another record with the same name already exists."))
