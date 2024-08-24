# -*- coding: utf-8 -*-

from odoo import models, fields


class city(models.Model):
    _name = 'ab_city'
    _description = 'city'
    name = fields.Char()
    state_id = fields.Many2one('res.country.state', 'State')
    _sql_constraints = [
        ('unique_City_name', 'unique (name)', 'Name must be unique!'),
    ]
