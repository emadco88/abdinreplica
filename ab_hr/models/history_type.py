from odoo import fields, models, api
from odoo.exceptions import UserError
import datetime
from .extra_functions import get_modified_name


class ActionTypeHistory(models.Model):
    _name = 'ab_hr_history_action_type'
    _description = 'ab_hr_history_action_type'
    name = fields.Char(required=True)
    type = fields.Selection(selection=[('1', 'New Job'),
                                       ('2', 'Modify Job'),
                                       ('3', 'New Manpower'),
                                       ('4', 'Modify Manpower'),
                                       ], default='1')

    invisible_job_title = fields.Boolean(default=True)
    invisible_workplace = fields.Boolean(default=True)
    invisible_job_id = fields.Boolean(default=False)

    action_date_type = fields.Selection(
        selection=[('hiring', 'Hiring'),
                   ('firing', 'Firing'),
                   ('pending_issue', 'Pending Issue'),
                   ('direct_issue', 'Direct Issue'),
                   ('clear_issue', 'Clear Issue'),
                   ('clear_firing', 'Clear Firing'),
                   ('no_effect', 'No Effect'),
                   ]
        , default='no_effect')

    feedback_action = fields.Boolean(default=False, string='Feedback Exit Action')

    # history security
    personnel_allowed = fields.Boolean(default=False)
    recruiter_allowed = fields.Boolean(default=False)
    payroll_entry_allowed = fields.Boolean(default=False)

    is_overlapped = fields.Boolean(default=False)

    manpower_effect = fields.Boolean(compute='_compute_manpower_effect', store=True)
    manpower_effect_type = fields.Selection(selection=[('increase', 'Increase'),
                                                       ('decrease', 'Decrease'),
                                                       ('double_effect', 'Double Effect'),
                                                       ('no_effect', 'No Effect'), ], )

    allowed_delay = fields.Integer(default=0, string='Recruitment Delay Limit')

    @api.depends('invisible_job_title', 'invisible_workplace', 'action_date_type')
    def _compute_manpower_effect(self):
        for rec in self:
            if (rec.invisible_job_title
                    and rec.invisible_workplace
                    and rec.action_date_type not in ['pending_issue', 'direct_issue', 'clear_issue']):
                rec.manpower_effect = False
            else:
                rec.manpower_effect = True

    @api.onchange('invisible_job_id')
    def _onchange_invisible_job_id(self):
        for rec in self:
            if rec.invisible_job_id:
                rec.invisible_workplace = False
                rec.invisible_job_title = False

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
