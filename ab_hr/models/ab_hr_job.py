from odoo import api, fields, models
from .extra_functions import get_modified_name


class Job(models.Model):
    _name = 'ab_hr_job'
    _description = 'ab_hr_job'

    name = fields.Char(required=True)
    access_history_user_ids = fields.Many2many('res.users', domain=[('share', '=', False)])
    internal_job = fields.Boolean(default=True)
    active = fields.Boolean(default=True)

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
        ('ab_hr_job_unique', 'unique(name)', 'JOB CAN NOT BE DUPLICATED!')]
