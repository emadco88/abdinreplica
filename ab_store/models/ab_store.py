from odoo import api, fields, models


class Store(models.Model):
    _name = 'ab_store'
    _description = 'Store'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    status = fields.Selection(selection=[('internal', 'Internal'),
                                         ('external', 'External')],
                              default='internal')
    store_type = fields.Selection(selection=[('main', 'Main'),
                                             ('branch', 'Branch'),
                                             ('store', 'Store'),
                                             ('internal_store', 'Internal Store'), ],
                                  default='branch')
    location = fields.Char()
    telephone = fields.Char()
    active = fields.Boolean(default=True)
    allow_purchase = fields.Boolean(default=True)
    allow_sale = fields.Boolean(default=True)
    allow_transfer = fields.Boolean(default=True)
    allow_replication = fields.Boolean(default=True)
    ip1 = fields.Char()
    ip2 = fields.Char()
    ip3 = fields.Char()
    ip4 = fields.Char()
    parent_id = fields.Many2one('ab_store')
    last_update_date = fields.Datetime()
    max_trans_value = fields.Float()

    _sql_constraints = [
        ('ab_store_name_unique', 'unique(name)', 'NAME CAN NOT BE DUPLICATED.'),
        ('ab_store_code_unique', 'unique(code)', 'CODE CAN NOT BE DUPLICATED.'),
    ]

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        code_args = args + [('code', '=', name), ]
        ids = self._search(code_args, limit=limit,
                           access_rights_uid=name_get_uid)
        if not ids:
            args += [('name', operator, name), ]
            ids = self._search(args, limit=limit,
                               access_rights_uid=name_get_uid)
        return ids

    # def create(self, vals):
    #     return super(Store, self).create(vals)
    #
    # def write(self, vals):
    #     return super(Store, self).write(vals)
    #
    # def unlink(self):
    #     return super(Store, self).unlink()
