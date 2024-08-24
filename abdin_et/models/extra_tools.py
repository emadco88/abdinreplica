from odoo import fields, models, api
import unicodedata
import re
import datetime


class ExtraTools(models.AbstractModel):
    _name = 'abdin_et.extra_tools'
    _description = 'Extra Tools'

    ##############################################################################################################
    def sh_msg(self, title='Done', message='Done', message_type='html', mode='ok',
               model_name=None, fn_method=None, *args, **kwargs
               ):
        context = dict(self._context or {})
        context[message_type] = message
        context['model_name'] = model_name
        context['mode'] = mode
        context['fn_method'] = fn_method
        context.update(kwargs)

        try:
            view_id = self.env.ref('sh_message.sh_message_wizard').id
        except ValueError:
            view_id = False

        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            "views": [(view_id, "form")],
            "view_id": view_id,
            'target': 'new',
            "context": context,
        }

    ##############################################################################################################
    @staticmethod
    def notify_user(msg, title="Error", msg_type="danger"):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': msg,
                'type': msg_type,  # types: success,warning,danger,info
                'sticky': True,  # True/False will display for few seconds if false
            },
        }

    ##############################################################################################################
    @staticmethod
    def slugify(value):
        value = str(value)
        value = unicodedata.normalize('NFKC', value)
        value = re.sub(r'[^\w\s-]', ' ', value.lower())
        return value

    ##############################################################################################################
    @staticmethod
    def get_modified_name(name):
        replacement = 'أإآ'
        for s in replacement:
            name = name.replace(s, 'ا')

        name = name.replace('ؤ', 'و')
        name = name.replace('ى', 'ي')
        name = name.replace('  ', '%')
        return name

    ##############################################################################################################
    @staticmethod
    def last_day_of_month(any_date):
        # this will never fail
        # get close to the end of the month for any day, and add 4 days 'over'
        next_month = any_date.replace(day=28) + datetime.timedelta(days=4)
        # subtract the number of remaining 'overage' days to get last day of current month
        # , or said programmaticaly said, the previous day of the first of next month
        return next_month - datetime.timedelta(days=next_month.day)
