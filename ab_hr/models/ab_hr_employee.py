# -*- coding: utf-8 -*-
import datetime
import itertools

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .extra_functions import get_modified_name


class Employees(models.Model):
    _name = 'ab_hr_employee'
    _description = 'ab_hr_employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    costcenter_id = fields.Many2one('ab_costcenter', index=True,
                                    readonly=lambda self: not self.user.has_group(
                                        'ab_hr.group_ab_hr_co')
                                    )
    mobile_phone = fields.Char('Work Mobile')
    work_email = fields.Char('Work Email')
    user_id = fields.Many2one('res.users', string='Related User', groups='base.group_system')
    work_phone = fields.Char(groups='ab_hr.group_ab_hr_co,ab_hr.group_ab_hr_secretary')
    cc_id = fields.Many2one('ab_costcenter')

    parent_id = fields.Many2one('ab_hr_employee', string='Manager',
                                compute="_compute_parent_id",
                                readonly=False,
                                store=True, )

    parent_department_id = fields.Many2one(related='department_id.parent_id', string='Superior Department')
    accid = fields.Char(related='costcenter_id.code', string='ePlus Code')
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.",
                          groups="base.group_user", copy=False)
    bc_id = fields.Integer(related='costcenter_id.bc_id', string='ePlus ID')
    user_line_owner = fields.Many2one('res.users', domain=lambda self: [('account_auth_ids', '!=', False)], )
    payment_name = fields.Char(groups='ab_hr.group_ab_hr_co,ab_hr.group_ab_hr_payroll_accountant')
    payment_no = fields.Char(groups='ab_hr.group_ab_hr_co,ab_hr.group_ab_hr_payroll_accountant')
    english_name = fields.Char()
    religion = fields.Selection(selection=[('muslim', 'Muslim'), ('christian', 'Christian'), ('other', 'Other'), ])
    graduate = fields.Char()
    gender = fields.Selection(
        selection=[('male', 'Male'),
                   ('female', 'Female'),
                   ], )

    identification_id = fields.Char(
        groups='ab_hr.group_ab_hr_co,ab_hr.group_ab_hr_personnel_spec,ab_hr.group_ab_hr_payroll_accountant')
    birthday = fields.Date(
        groups='ab_hr.group_ab_hr_co,ab_hr.group_ab_hr_personnel_spec,ab_hr.group_ab_hr_payroll_accountant')

    # One2many fields
    job_occupied_ids = fields.One2many(comodel_name='ab_hr_job_occupied', inverse_name='employee_id', readonly=True)
    emp_history_ids = fields.One2many(comodel_name='ab_hr_emp_history', inverse_name='employee_id')
    emp_doc_status_ids = fields.One2many(comodel_name='ab_hr_emp_doc_status', inverse_name='employee_id')

    # COMPUTED FIELDS
    job_id = fields.Many2one('ab_hr_job', store=True, compute='_compute_job_department', readonly=True)
    department_id = fields.Many2one('ab_hr_department', store=True, compute='_compute_job_department', readonly=True)
    mod_name = fields.Char(compute='_compute_mod_name', store=True)
    is_docs_complete = fields.Boolean(compute='_compute_is_docs_complete')
    is_working = fields.Boolean(compute='_compute_is_working', search='_search_is_working')

    address_text = fields.Char(string='Address: ')
    khazna_subscription = fields.Boolean(default=False, groups='ab_hr.group_ab_hr_co')
    active = fields.Boolean(default=True)
    # insurance Fields
    insurance_info_ids = fields.One2many('ab_hr_insurance_info', inverse_name='employee_id')
    insurance_status = fields.Boolean(store=True, )
    insurance_type = fields.Selection(selection=[('abdin', 'Abdin Pharmacies'), ('other', 'Other')])
    insurance_branch = fields.Char()
    insurance_no = fields.Char()
    insurance_start = fields.Date()
    internal_working_employee = fields.Boolean(compute='_compute_internal_working_employee',
                                               search='_search_internal_working_employee')

    @api.depends('department_id.manager_id', 'department_id.parent_id.manager_id', 'job_occupied_ids')
    def _compute_parent_id(self):
        for rec in self:
            if rec.department_id.manager_id and rec.department_id.manager_id.id != rec.id:
                rec.parent_id = rec.department_id.manager_id.id

    @api.depends('job_id')
    def _compute_is_working(self):
        for rec in self:
            rec.is_working = bool(rec.job_id)

    def _search_is_working(self, operator, val):
        if operator not in ['=', '!='] or not isinstance(val, bool):
            raise UserError(_('Operation not supported'))
        self.flush()
        sql = """
            select distinct employee_id from ab_hr_job_occupied job 
                where job.termination_date is null
        """
        self.env.cr.execute(sql)
        employees = self.env.cr.fetchall()
        employee_ids = list(itertools.chain.from_iterable(employees))
        if operator != '=':  # that means it is '!='
            val = not val
        return [('id', 'in' if val else 'not in', employee_ids)]

    @api.depends('job_id')
    def _compute_internal_working_employee(self):
        for rec in self:
            curr_job = rec.job_occupied_ids.filtered(lambda job: job.job_id.internal_job and not job.termination_date)
            rec.internal_working_employee = bool(curr_job)

    def _search_internal_working_employee(self, operator, val):
        if operator not in ['=', '!='] or not isinstance(val, bool):
            raise UserError(_('Operation not supported'))
        self.flush()
        sql = """
            select distinct employee_id 
            from ab_hr_job_occupied job
            left join ab_hr_job hj on job.job_id = hj.id
                where job.termination_date is null and hj.internal_job=True 
        """
        self.env.cr.execute(sql)
        employees = self.env.cr.fetchall()
        employee_ids = list(itertools.chain.from_iterable(employees))
        if operator != '=':  # that means it is '!='
            val = not val
        return [('id', 'in' if val else 'not in', employee_ids)]

    @api.depends('emp_doc_status_ids')
    def _compute_is_docs_complete(self):
        #  doc.status are (missing, existing, excluded, temp_excluded)
        for rec in self:
            is_docs_complete = False
            for doc in rec.emp_doc_status_ids:
                is_doc_expired = doc.expiry_date and doc.expiry_date < datetime.date.today()
                is_doc_missing = doc.status == 'missing'
                if is_doc_missing or is_doc_expired:
                    is_docs_complete = False
                    break
                else:
                    is_docs_complete = True
            rec.is_docs_complete = is_docs_complete

    @api.depends('name')
    def _compute_mod_name(self):
        for rec in self:
            rec.mod_name = get_modified_name(rec.name)

    _sql_constraints = [
        ('ab_hr_employees_employee_unique', 'unique(costcenter_id)', 'Employee CAN NOT BE DUPLICATED!')]

    @api.depends('job_occupied_ids')
    def _compute_job_department(self):
        # employees = self.env['ab_hr_employee'].search([])
        for rec in self:
            if not rec.job_occupied_ids:
                rec.job_id = False
                rec.department_id = False
            active_jobs = rec.job_occupied_ids.filtered(
                lambda r: r.job_status == 'active' and r.is_main_job and r.job_id.internal_job)
            if active_jobs:
                rec.job_id = active_jobs[0].job_id.id
                rec.department_id = active_jobs[0].workplace.id
            else:
                rec.job_id = False
                rec.department_id = False

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        mod_name = get_modified_name(name)
        args += ['|', '|',
                 ('mod_name', operator, mod_name),
                 ('name', operator, name),
                 ('accid', '=ilike', name),
                 ]

        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return ids

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        vals = []
        docs = self.env['ab_hr_emp_doc'].search([])

        for doc in docs:
            vals.append((0, 0, {'emp_doc_id': doc.id, 'status': 'missing'}))
        res.update({'emp_doc_status_ids': vals})
        return res

    def btn_add_docs(self):
        docs = self.env['ab_hr_emp_doc'].search([])
        self.ensure_one()

        for doc in docs:

            if doc.id not in self.emp_doc_status_ids.mapped('emp_doc_id.id'):
                self.emp_doc_status_ids.create({'emp_doc_id': doc.id, 'status': 'missing'})

    def btn_add_job(self):

        return {
            'name': _("Create New Job"),
            'type': 'ir.actions.act_window',
            'res_model': 'ab_hr_job_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
                'default_type_of_action': '1',
            }
        }

    def btn_update_user_name(self):
        if self.env.user.has_group('base.group_system'):
            self.user_id.name = self.name
