from odoo import api, fields, models, _


class AbSupplierBracket(models.Model):
    _name = 'ab_supplier_bracket'
    _description = 'ab_supplier_bracket'
    _rec_name = 'payment_type_id'

    payment_type_id = fields.Many2one('ab_supplier_payment_type')
    payment_type = fields.Selection(
        selection=[('credit', 'Credit'),
                   ('claim_cash', 'Claim Cash'),
                   ('instant_cash', 'Instant Cash'),
                   ], )

    supplier_id = fields.Many2one('ab_costcenter')
    start_day = fields.Integer(default=0, required=True)
    credit_days = fields.Integer()
    discount = fields.Float(digits=(5, 2))
    withdrawal_bracket = fields.Float(default=0.0, required=True)

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, f"{rec.supplier_id.name} [{rec.payment_type_id.name}]"))
        return res
