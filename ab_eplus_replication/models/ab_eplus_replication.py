import decimal
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

PARAM_STR = '%s'
METHODS_MAP = {
    'ab_product': 'replicate_ab_product',
    'ab_store': 'replicate_ab_store',
    'ab_supplier': 'replicate_ab_supplier',
    'ab_purchase_header': 'replicate_ab_purchase_header',
    'ab_purchase_line': 'replicate_ab_purchase_line',
    'ab_purchase_notice_header': 'replicate_purchase_returns',
}


def _is_new_value(record, field, new_value):
    old = getattr(record, field)
    if hasattr(old, 'ids'):
        if type(new_value) == list:
            # [(6, 0, [1])]
            old_value = [(6, 0, getattr(record, field).ids)]
        else:
            old_value = getattr(record, field).id
    elif isinstance(old, (float, decimal.Decimal)):
        old_value = round(float(old), 2)
        new_value = round(float(new_value), 2)
    else:
        old_value = old

    not_same_value = (old_value != new_value)
    return not_same_value


class Replication(models.AbstractModel):
    _name = 'ab_eplus_replication'
    _description = 'ab_eplus_replication'
    _inherit = 'ab_eplus_connect'

    METHODS_MAP = METHODS_MAP

    def _get_or_create_record(self, model_dict, model_name, update_target=None):
        model = self.env[model_name].sudo()

        record = model.with_context(active_test=False).search(
            [('eplus_serial', '=', model_dict['eplus_serial'])])

        if update_target:
            model_dict.pop('last_update_date', None)

        if record:
            values = {field: value for field, value in model_dict.items()
                      if _is_new_value(record, field, value)}

            if values:
                record.with_context(eplus_replication=True).write(values)
        elif not update_target:
            record = model.with_context(eplus_replication=True).create(model_dict)

        return record

    def _get_or_replicate_record(self, model_name, eplus_serial, **kw):
        _model = self.env[model_name].sudo()

        record = _model.with_context(active_test=False).search([('eplus_serial', '=', eplus_serial)], limit=1)
        if not record:
            method_name = METHODS_MAP.get(model_name)
            # run method using self attribute
            getattr(self, method_name)(**kw)

            record = _model.with_context(active_test=False).search([('eplus_serial', '=', eplus_serial)], limit=1)

        if not record:
            _logger.info(f"model_name: {model_name} --- eplus_serial: {eplus_serial}")
            raise ValidationError(_(f"REPLICATION ERROR {model_name}-{eplus_serial}"))

        return record

    def _get_last_update_date(self, model_name, store_id=None):
        domain = [('last_update_date', '!=', False)]
        if store_id:
            domain += [('store_id', '=', store_id)]

        model_line = self.env[model_name].sudo().with_context(active_test=False).search(domain,
                                                                                        order='last_update_date DESC',
                                                                                        limit=1)
        last_update_date = model_line.last_update_date

        if last_update_date:
            return last_update_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        else:
            return None

    @api.model
    def _get_where_condition(self, last_update_date):
        where_condition = (
                last_update_date
                and f" WHERE IIF(main.sec_update_date is NULL,main.sec_insert_date,main.sec_update_date)>={PARAM_STR} "
                or " WHERE (1=1) ")
        return where_condition

    def _fetch_eplus_data(self, sql, last_update_date, xrows=10000, server=None):
        with self.connect_eplus(param_str=PARAM_STR, server=server) as conn:
            with conn.cursor(as_dict=True) as cr:
                params = tuple([last_update_date]) if last_update_date else tuple()
                cr.execute(sql, params)

                while True:
                    rows = cr.fetchmany(xrows)
                    if not rows:
                        break
                    yield rows

    @staticmethod
    def _is_new_value(record, field, new_value):
        return _is_new_value(record, field, new_value)

    def get_store(self, eplus_serial):
        return self._get_or_replicate_record(model_name='ab_store', eplus_serial=eplus_serial)

    def get_supplier(self, eplus_serial):
        return self._get_or_replicate_record(model_name='ab_supplier', eplus_serial=eplus_serial)

    def get_product(self, eplus_serial):
        return self._get_or_replicate_record(model_name='ab_product', eplus_serial=eplus_serial)
