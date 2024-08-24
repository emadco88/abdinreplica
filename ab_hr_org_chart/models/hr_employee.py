# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Employee(models.Model):
    _inherit = ["ab_hr_employee"]

    subordinate_ids = fields.One2many('ab_hr_employee', string='Subordinates', compute='_compute_subordinates',
                                      help="Direct and indirect subordinates",
                                      compute_sudo=True)
