import math

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import re


class AbdinProduct(models.Model):
    _name = 'ab_product'
    _description = 'Abdin Product'

    product_card_id = fields.Many2one('ab_product_card', required=True, delegate=True, ondelete='restrict')
    product_card_name = fields.Char(related='product_card_id.name', readonly=False, string="Name")
    name = fields.Char(compute='_compute_product_name', store=True, readonly=True, string="Full Name")
    default_price = fields.Float(digits=(16, 2), default=0)
    default_cost = fields.Float(digits=(16, 2), default=0)
    tag_ids = fields.Many2many(comodel_name='ab_product_tag', relation='ab_product_product_tag', column1='product_id',
                               column2='tag_id')
    barcode_ids = fields.Many2many(comodel_name='ab_product_barcode', relation='ab_product_barcode_rel',
                                   column1='product_id', column2='barcode_id')
    unit_l_id = fields.Many2one('ab_uom', domain=[('unit_size', '=', 'large')], required=True)
    unit_m_id = fields.Many2one('ab_uom', domain=[('unit_size', '=', 'medium')], required=True)
    unit_s_id = fields.Many2one('ab_uom', domain=[('unit_size', '=', 'small')], required=True)
    uom_ids = fields.Many2many('ab_uom', compute='_compute_uom_ids')
    allow_sale = fields.Boolean(default=True)
    allow_purchase = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    code = fields.Char()

    @api.depends('unit_l_id', 'unit_m_id', 'unit_s_id')
    def _compute_uom_ids(self):
        for rec in self:
            rec.uom_ids = self.env['ab_uom'].sudo().search([('id', 'in', [
                rec.unit_l_id.id,
                rec.unit_m_id.id,
                rec.unit_s_id.id,
            ])])

    def qty_from_small(self, qty, unit_size):
        """
         :param unit_size: 'large', 'medium' or 'small'
         :param qty: absolute final inventory quantity
         :return: convert from small qty to other units.
         """
        if not (self and qty and unit_size):
            return 0

        self.ensure_one()
        unit_s_no = self.unit_s_id.unit_no
        unit_m_no = self.unit_m_id.unit_no
        if not (qty / unit_m_no).is_integer():
            raise ValidationError(_("CONVERTING FROM SMALL ERROR: SMALL QTY INCONSISTENT WITH MEDIUM QTY, "
                                    "Product ID: %s" % self.id))

        if unit_size == 'large':
            return qty / unit_s_no
        elif unit_size == 'medium':
            return qty * unit_m_no / unit_s_no
        else:  # 'small'
            return qty

    def qty_to_small(self, qty, unit_size):
        """
         :param unit_size: 'large', 'medium' or 'small'
         :param qty: absolute final inventory quantity
         :return: convert qty from other units to small.
         """
        if not (self and qty and unit_size):
            return 0

        self.ensure_one()
        unit_s_no = self.unit_s_id.unit_no
        unit_m_no = self.unit_m_id.unit_no
        # Consider Medium Unit
        if abs(int((qty * unit_m_no)) - qty * unit_m_no) > 0.1:
            raise ValidationError(_("CONVERTING TO SMALL ERROR: SMALL QTY INCONSISTENT WITH MEDIUM QTY, "
                                    "Product ID: %s" % self.id))

        if unit_size == 'large':
            qty_in_small = qty * unit_s_no
        elif unit_size == 'medium':
            qty_in_small = (qty * unit_s_no) / unit_m_no
        else:
            qty_in_small = qty

        # @todo FIX this
        qty_in_small = round(qty_in_small)

        return qty_in_small

    def btn_edit_product_main_data(self):
        self.ensure_one()
        return {
            'view_mode': 'form',
            'res_model': 'ab_product_card',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.product_card_id.id,
            'views': [[False, 'form']]
        }

    @api.model
    def validate_product_units(self, unit_s_id, unit_m_id, unit_l_id):
        """
        Make this function separated from constrains as we need to use it in other modules (e.g., ab_eplus_replication)
        """

        if unit_s_id.unit_no == 1 and unit_m_id.unit_no > 1:
            raise ValidationError(
                _("Incorrect unit division. "
                  "Please ensure the unit number of the medium unit is not greater than 1 "
                  "when the small unit number is 1."))

        division = round(unit_s_id.unit_no /
                         unit_m_id.unit_no, 5)

        if not division.is_integer():
            raise ValidationError(
                _("Incompatible division between medium and small units. "
                  "Please ensure the division result is an integer."))

        if unit_m_id.type_id.id == unit_l_id.type_id.id and unit_m_id.unit_no > 1:
            raise ValidationError(
                _("Medium unit type must be different from large unit type. "
                  "Please ensure the medium unit number is not greater than 1 "
                  "when the type IDs of medium and large units are the same."))

    @api.constrains('unit_m_id', 'unit_s_id', 'unit_l_id')
    def constrains_product(self):
        if self.env.context.get('eplus_replication'):
            return
        for record in self:
            self.validate_product_units(record.unit_s_id, record.unit_m_id, record.unit_l_id)

    @api.depends('product_card_id.name', 'tag_ids.name')
    def _compute_product_name(self):
        for rec in self:
            rec.name = f"{rec.product_card_id.name} {', '.join(tag.name for tag in rec.tag_ids.sorted('priority'))}"

    def _add_unit_tag(self, record):
        tag_model = self.env['ab_product_tag']
        if record.unit_s_id.unit_no == 1 or record.unit_s_id.id == record.unit_m_id.id:
            tag_name = f"{record.unit_s_id.unit_no} {record.unit_s_id.type_id.name}"
        else:
            tag_name = f"{record.unit_m_id.unit_no} {record.unit_m_id.type_id.name} {record.unit_s_id.unit_no} {record.unit_s_id.type_id.name}"
        tag = tag_model.search([('name', '=', tag_name)], limit=1) or tag_model.create(
            {'name': tag_name, 'tag_type': 'unit'})
        record.write({'tag_ids': [(4, tag.id)]})

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        pattern = r"\*|  "
        new_name = re.sub(pattern, "%", name) + '%'
        domain = [('name', '=ilike', new_name)] + args
        if name:
            product_ids = self.search(
                ['|', ('barcode_ids', '=ilike', name), ('code', '=ilike', name)])
            if product_ids:
                domain = [('id', 'in', product_ids.ids)] + args
        return self._search(domain, limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def create(self, vals_list):
        record = super().create(vals_list)
        self._add_unit_tag(record)
        return record

    def write(self, vals):
        for rec in self:
            old_units = (rec.unit_m_id.unit_no, rec.unit_m_id.type_id.id,
                         rec.unit_s_id.unit_no, rec.unit_s_id.type_id.id)
            res = super().write(vals)
            new_units = (rec.unit_m_id.unit_no, rec.unit_m_id.type_id.id,
                         rec.unit_s_id.unit_no, rec.unit_s_id.type_id.id)
            if old_units != new_units:
                rec.write({'tag_ids': [(3, tag.id)
                                       for tag in rec.tag_ids if not tag.tag_type]})
                self._add_unit_tag(rec)
            return res
