# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models, _


class sh_message_wizard(models.TransientModel):
    _name = "sh.message.wizard"
    _description = "Message wizard to display warnings, alert ,success messages"

    def get_default(self, msg_type):
        if self.env.context.get(msg_type, False):
            return self.env.context.get(msg_type)
        else:
            return False

    name = fields.Text(string="Message", readonly=True, default=lambda self: self.get_default('message'))
    text = fields.Text(string="Text", readonly=True, default=lambda self: self.get_default('text'))
    html = fields.Html(string="HTML", readonly=True, default=lambda self: self.get_default('html'))
    mode = fields.Char(string='Mode', readonly=True, default=lambda self: self.get_default('mode'))

    def fn_method(self, *args, **kwargs):
        kwargs.update(self.env.context)
        model_name = kwargs.get('model_name', False)
        fn_method = kwargs.get('fn_method', False)
        if model_name and fn_method:
            fn_method = getattr(self.env[model_name], fn_method)
            return fn_method(*args, **kwargs)
        else:
            pass
            # return {'type': 'ir.actions.act_window_close'}
