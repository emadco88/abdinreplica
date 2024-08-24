# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from .extra_functions import get_modified_name


class Departments(models.Model):
    _name = 'ab_hr_department'
    _description = 'ab_hr_department'

    name = fields.Char(required=True)
    manager_id = fields.Many2one('ab_hr_employee',
                                 compute='_compute_manager_id',
                                 string='Department Manager',
                                 store=True,
                                 domain=[
                                     ('is_working', '=', True),
                                     ('internal_working_employee', '=', True),
                                 ])

    parent_id = fields.Many2one('ab_hr_department', 'Superior Department')

    workplace_region = fields.Many2one('ab_hr_region')
    manpower_ids = fields.One2many('ab_hr_manpower', inverse_name='workplace')
    active = fields.Boolean(default=True)
    job_title_ids = fields.Many2many(
        comodel_name='ab_hr_job',
        relation='ab_hr_job_department_rel',
        column1='department_id',
        column2='job_title_id',
        string='Managerial Job Titles')

    occupied_job_ids = fields.One2many(
        "ab_hr_job_occupied",
        "workplace")

    store_id = fields.Many2one('ab_store', index=True)
    user_id = fields.Many2one('res.users', groups='base.group_system')

    @api.depends('occupied_job_ids', 'occupied_job_ids.workplace', 'occupied_job_ids.job_status',
                 'occupied_job_ids.job_id', 'job_title_ids')
    def _compute_manager_id(self):
        for rec in self:
            workplace_id = rec.id
            job_title_ids = rec.job_title_ids.ids
            occupied_job = rec.occupied_job_ids.filtered(
                lambda job: (
                        job.job_id.id in job_title_ids
                        and job.workplace.id == workplace_id
                        and job.job_status == 'active'
                ))

            if occupied_job:
                rec.manager_id = occupied_job[0].employee_id.id
            else:
                rec.manager_id = False

    def btn_add_job_title(self):
        return {
            'name': _("Create New Job"),
            'type': 'ir.actions.act_window',
            'res_model': 'ab_hr_job_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_workplace': self.id,
                'default_type_of_action': '3',
            }
        }

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

    _sql_constraints = [
        ('ab_hr_department_unique', 'unique(name)', 'DEPARTMENT CAN NOT BE DUPLICATED!')]
