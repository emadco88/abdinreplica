from odoo import models

PARAM_STR = "%s"


class ReplicationStore(models.AbstractModel):
    _inherit = 'ab_eplus_replication'

    def replicate_ab_store(self, replicate_all=False, update_target=None, xrows=10000, commit=False, where_extra_and="",
                           **kw):
        if replicate_all:
            last_update_date = None
        else:
            last_update_date = self._get_last_update_date(model_name='ab_store')

        stores = self._get_stores_from_bconnect(last_update_date, xrows, where_extra_and=where_extra_and)

        for i, chunk_of_stores in enumerate(stores):
            msg = f"Replicating stores Part {i}"
            self._start_stores_replication(chunk_of_stores, msg=msg, update_target=update_target)
            if commit:
                self.env.cr.commit()

    def _get_stores_from_bconnect(self, last_update_date, xrows, where_extra_and=""):
        where_condition = self._get_where_condition(last_update_date)
        where_condition += where_extra_and
        sql = f"""
            Select main.sto_code,
            main.sto_name_ar,
            main.sto_ip1,
            main.sto_ip2,
            IIF(main.sec_update_date is NULL,main.sec_insert_date,main.sec_update_date) as last_update_date,
            main.sto_id as eplus_serial,
            main.activated
            from store main         
            {where_condition}
         order by last_update_date
         """

        yield from self._fetch_eplus_data(sql, last_update_date, xrows)

    def _start_stores_replication(self, stores, msg="Replicating Stores", **kw):
        for item in self.web_progress_iter(stores, msg=msg):
            active = True

            # store exists
            item_exists_by_code = self.env['ab_store'].sudo().with_context(active_test=False).search(
                [('code', '=', item['sto_code'])]
            )
            if item_exists_by_code:
                # Must set eplus_serial 'MANUALLY' if not set
                if not item_exists_by_code.eplus_serial:
                    continue
                else:
                    # keep store active value
                    active = item_exists_by_code.active
            # New Internal Store
            elif item['activated'] != '2':
                active = False

            store_dict = {
                "code": item['sto_code'],
                "name": item['sto_name_ar'],
                "ip1": item['sto_ip1'],
                "ip2": item['sto_ip2'],
                "last_update_date": item['last_update_date'],
                "eplus_serial": item['eplus_serial'],
                "active": active,
            }
            self._get_or_create_record(store_dict, model_name='ab_store', **kw)
