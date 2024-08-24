# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from .extra_functions import get_modified_name


######################################################################################################################
class EmployeeJobs(models.Model):
    _name = 'ab_hr_job_occupied'
    _description = 'Employee Jobs'
    _rec_name = 'job_id'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'abdin_et.extra_tools']

    employee_id = fields.Many2one('ab_hr_employee', required=True, index=True, string='Employee', tracking=True)
    accid = fields.Char(related='employee_id.accid', string="Code", tracking=True)
    internal_working_employee = fields.Boolean(related='employee_id.internal_working_employee', )
    is_working = fields.Boolean(related='employee_id.is_working', )
    job_id = fields.Many2one('ab_hr_job', required=True, index=True, tracking=True, string="Job Title")
    child_ids = fields.One2many('ab_hr_job_occupied', inverse_name='parent_id', string='Direct subordinates')

    action_date = fields.Date()
    workplace = fields.Many2one('ab_hr_department', required=True, tracking=True)
    job_status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')],
                                  compute='_compute_job_status',
                                  store=True)
    hiring_date = fields.Date(tracking=True)
    termination_date = fields.Date(tracking=True)

    issue_date = fields.Date(compute="_compute_issue_date", store=True, tracking=True)

    territory = fields.Selection(selection=[('1', 'North'), ('2', 'South'), ('3', 'Both')], tracking=True)
    region = fields.Char(tracking=True)
    workplace_region = fields.Many2one(related='workplace.workplace_region', tracking=True)
    default_salary = fields.Float(groups="ab_hr.group_ab_hr_payroll_entry", tracking=True)
    is_main_job = fields.Boolean(default=True, tracking=True)
    history_ids = fields.One2many(comodel_name='ab_hr_emp_history', inverse_name='job_id')

    parent_id = fields.Many2one('ab_hr_employee', string='Manager',
                                compute="_compute_parent_id",
                                store=True, )

    parent_department_id = fields.Many2one(related='workplace.parent_id', string='Superior Department')

    @api.depends('workplace.manager_id', 'workplace.parent_id.manager_id')
    def _compute_parent_id(self):
        for rec in self:
            if rec.workplace.manager_id and rec.workplace.manager_id.id != rec.employee_id.id:
                rec.parent_id = rec.workplace.manager_id
            else:
                rec.parent_id = rec.workplace.parent_id.manager_id

    @api.depends('history_ids.action_date', 'history_ids.action_type')
    def _compute_issue_date(self):
        history = self.env['ab_hr_emp_history'].sudo()
        for job in self:
            # if job(<NewId origin=xxx>,) continue
            if not job.id:
                continue

            history_ids = history.search([('job_id', '=', job.id)], order='action_date desc')
            for history_id in history_ids:
                if history_id.action_type.action_date_type in ['clear_issue']:
                    job.sudo().issue_date = None
                    break
                elif history_id.action_type.action_date_type in ['pending_issue', 'direct_issue']:
                    job.sudo().issue_date = history_id.action_date
                    break
            else:
                job.sudo().issue_date = None

    def _get_selection_from_action_type(self):
        model = self.env['ab_hr_history_action_type']
        selection = model.fields_get(allfields=['type'])['type']['selection']
        return selection

    @api.depends('termination_date')
    def _compute_job_status(self):
        for rec in self:
            if rec.termination_date:
                rec.job_status = 'inactive'
            else:
                rec.job_status = 'active'

    def write(self, values):
        model = self.env['ab_hr_employee']
        emp_ids = self.mapped('employee_id.id')

        res = super().write(values)
        if values:
            if values.get('employee_id', False):
                emp_ids.append(values.get('employee_id'))
        self.env.all.tocompute[model._fields['department_id']].update(emp_ids)
        model.recompute()
        return res

    @api.constrains('employee_id', 'job_id', 'workplace', 'job_status')
    def ab_hr_job_occupied_constrains(self):
        for rec in self:
            if rec.job_status == 'active':
                job = self.env['ab_hr_job_occupied'].search([
                    ('id', '!=', rec.id),
                    ('job_status', '=', 'active'),
                    ('employee_id', '=', rec.employee_id.id),
                    ('job_id', '=', rec.job_id.id),
                    ('workplace', '=', rec.workplace.id),
                ], limit=1)

                if job and job[0]:
                    raise ValidationError("""Duplicated active job for the same employee
                    \nName: %s\n Job Title: %s\n Workplace: %s\n Hiring Date: %s\n Region: %s\n""" % (
                        job.employee_id.name,
                        job.job_id.name,
                        job.workplace.name,
                        job.hiring_date,
                        job.region,
                    ))

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s/%s/%s' % (
                rec.employee_id.name, rec.job_id.name, rec.workplace.name,)))
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        mod_name = get_modified_name(name)
        args += ['|', '|',
                 ('employee_id.name', operator, name),
                 ('job_id.name', operator, mod_name),
                 ('id', '=ilike', name),
                 ]

        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return ids

    def btn_change_job(self):

        return {
            'name': _("Add Movement"),
            'type': 'ir.actions.act_window',
            'res_model': 'ab_hr_job_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_job_id': self.id,
                'default_type_of_action': '2', }
        }
