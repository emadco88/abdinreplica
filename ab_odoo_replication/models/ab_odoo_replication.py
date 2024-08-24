# -*- coding: utf-8 -*-
import datetime
from odoo import models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import config
from .ab_odoo_connect import OdooConnectionPool
import logging

_logger = logging.getLogger(__name__)


def eval_val(val, ttype):
    if type(val) == list and ttype == 'many2one':
        return val[0]
    elif not ttype == 'boolean' and not val:
        return None
    else:
        return val


class OdooReplication(models.AbstractModel):
    _name = 'ab_odoo_replication'
    _description = 'ab_odoo_replication'

    _group_xml_ids = []

    def replicate_model(self, model_name: str, limit=10000, commit=False, extra_fields=None, replicate_all=False):
        pool = OdooConnectionPool(self.env)
        if model_name == 'res.users' and extra_fields and 'groups_id' in extra_fields:
            group_xml_ids = self.get_matching_xml_gid_list(pool)
            self._group_xml_ids.extend(group_xml_ids)

        model, uid, db, password = pool.get_connection()
        extra_fields = extra_fields or {}
        table_name = model_name.replace('.', '_')
        # pull_data
        if replicate_all:
            max_write_date = datetime.datetime(year=1999, month=1, day=1, hour=0, minute=0, second=0)
        else:
            max_write_date = self.env[model_name].with_user(SUPERUSER_ID).with_context(active_test=False).search(
                [], order="write_date desc", limit=1).write_date
            if not max_write_date:
                max_write_date = datetime.datetime(year=1999, month=1, day=1, hour=0, minute=0, second=0)

        offset = 0
        domain = [('write_date', '>=', max_write_date)]
        missing_many2one_flds = []

        # get updates_count
        server_updates_count = model.execute_kw(
            db, uid, password, model_name, 'search_count',
            [domain],
            {
                'context': {'active_test': False}  # Include non-active records
            }
        )

        parts = round(server_updates_count / limit)
        part = 0

        # get fields to replicate
        self.env.cr.execute(f"""
                        SELECT name, ttype,relation FROM ir_model_fields 
                        WHERE model=%s 
                        AND (store=true AND ttype NOT IN ('binary','many2many','one2many')) 
                        AND name not in 
                        ('last_update_date',
                        'message_main_attachment_id',
                        'accounting_auth_group_id')
                    """, (model_name,))

        fields_for_repl_rows = self.env.cr.fetchall()
        curr_fields = {row[0] for row in fields_for_repl_rows}
        curr_fields |= extra_fields.keys()

        fields_for_repl = {row[0]: row[1] for row in fields_for_repl_rows if row[1]}
        models_with_many2one = [(row[0], row[2]) for row in fields_for_repl_rows if row[1] == 'many2one']

        while True:
            part += 1
            fields_info = model.execute_kw(
                db, uid, password, model_name, 'fields_get',
                [],
                {'attributes': ['type']}
            )

            remote_fields = set(fields_info.keys())

            fields_to_get = list(curr_fields & remote_fields)
            server_updates = model.execute_kw(
                db, uid, password, model_name, 'search_read',
                [domain],
                {
                    'fields': fields_to_get,
                    'order': 'write_date, id',
                    'offset': offset,
                    'limit': limit,
                    'context': {'active_test': False}  # Include non-active records
                }
            )

            if not server_updates:
                break  # Exit the loop if there are no more records
            # write_date = 'write_date' if rec_id else '_________'
            for rec in self.web_progress_iter(server_updates, msg=f'replicating {model_name} Part {part}/{parts}'):
                self._replicate_main_fields(fields_for_repl,
                                            model_name,
                                            table_name,
                                            models_with_many2one,
                                            missing_many2one_flds,
                                            rec)

                if model_name == 'res.users':
                    user_id = rec.get('id', 0)
                    enc_pass = self._get_encrypted_password(pool, user_id)
                    if enc_pass:
                        user = self.env['res.users'].sudo().browse(user_id)
                        if user.password != enc_pass:
                            self.env.cr.execute("UPDATE res_users set password = %s WHERE id = %s",
                                                (enc_pass, user_id))

                self._replicate_extra_fields(extra_fields, model_name, rec)

            # commit fetched records [number of records = limit]
            if commit:
                self.env.cr.commit()

            offset += limit  # Move to the next batch
        self._replicate_missing_many2one(missing_many2one_flds, model_name, table_name)

    def _replicate_main_fields(self, fields_for_repl, model_name, table_name,
                               models_with_many2one, missing_many2one_flds, rec):

        rec_id = rec.get('id', 0)
        for missing_field, missing_model in models_with_many2one:
            many2one_rec_id = rec[missing_field] and rec[missing_field][0]
            if many2one_rec_id:
                rec_exist = self.env[missing_model].with_context(active_test=False).search([
                    ('id', '=', many2one_rec_id)
                ])
                if not rec_exist:
                    missing_many2one_flds.append((missing_model, missing_field, many2one_rec_id, rec_id))
                    rec[missing_field] = False

        fld_val_list = [(fld, eval_val(val, fields_for_repl[fld])) for fld, val in rec.items()
                        if fld in fields_for_repl]
        update_str = ','.join([f"{ss[0]}=%s" for ss in fld_val_list])
        insert_str = ','.join(fld[0] for fld in fld_val_list)
        vals_tuple = tuple(val[1] for val in fld_val_list)
        check_exist = self.env[model_name].with_context(active_test=False).search([
            ('id', '=', rec.get('id', 0))
        ])

        if model_name == 'res.users' and rec_id <= 5:
            return
        if model_name == 'res.partner' and rec_id <= 6:
            return
        if check_exist:
            sql = f"""UPDATE {table_name}
                      SET {update_str}
                      WHERE id=%s"""
            self.env.cr.execute(sql, vals_tuple + (rec.get('id'),))
        else:
            sql = f"""
               INSERT INTO {table_name}({insert_str})
               VALUES ({','.join(['%s'] * len(fld_val_list))})"""
            self.env.cr.execute(sql, vals_tuple)

    def _replicate_extra_fields(self, extra_fields, model_name, rec):
        for fld, ttype in extra_fields.items():
            if ttype == 'binary':
                self._replicate_binary_field(fld, model_name, rec)
            elif ttype == 'many2many':
                self._replicate_many2many_field(fld, model_name, rec)

    def _replicate_binary_field(self, fld, model_name, rec):
        rec_id = rec.get('id', 0)
        datas = rec.get(fld)
        if datas:
            attachment_mo = self.env['ir.attachment'].sudo()
            att = attachment_mo.search([
                ('res_field', '=', fld),
                ('res_model', '=', model_name),
                ('res_id', '=', rec_id),
            ])

            if att:
                att.write({'datas': datas})
            else:
                # Create an attachment in Odoo, storing the binary PDF data
                attachment_id = self.env['ir.attachment'].create({
                    'name': fld,
                    'type': 'binary',
                    'datas': datas,
                    'res_model': model_name,
                    'res_field': fld,
                    'res_id': rec_id,
                })

    def _replicate_many2many_field(self, fld, model_name, rec):
        self = self.with_context(replication=True)
        model = self.env[model_name].with_context(active_test=False).sudo()
        rec_id = rec.get('id', 0)
        other_ids = rec.get(fld)
        if model_name == 'res.users' and fld == 'groups_id':
            # {group['module']}.{group['name'] --> base.group_user, ab_hr.group_basic_data , ... etc
            other_xml_ids = [self.env.ref(f"{group['module']}.{group['name']}").id
                             for group in self._group_xml_ids
                             if group['res_id'] in other_ids]

            model.browse(rec_id).write({fld: [(6, 0, other_xml_ids)]})

        else:
            model.browse(rec_id).write({fld: [(6, 0, other_ids)]})

    def _replicate_missing_many2one(self, missing_many2one_flds, model_name, table_name):
        internal_many2one_flds = [(item[1], item[2], item[3])
                                  for item in missing_many2one_flds
                                  if item[0] == model_name]

        external_many2one_flds = [(item[1], item[2], item[3])
                                  for item in missing_many2one_flds
                                  if item[0] != model_name]
        # Replicating Internal Many2one fields
        for many2one_name, many2one_value, rec_id in internal_many2one_flds:
            self.env.cr.execute(f"""UPDATE {table_name} SET {many2one_name} = %s WHERE id = %s
                """, (many2one_value, rec_id))
        self.env.cr.execute(f"""SELECT setval ('{table_name}_id_seq', (SELECT MAX (id) FROM {table_name})+1);""")

        self.env.cr.commit()

        # Replicating External Many2one fields
        missing_models = {item[0] for item in missing_many2one_flds if item[0] != model_name}

        for mo in missing_models:
            self.replicate_model(mo)

        for many2one_name, many2one_value, rec_id in external_many2one_flds:
            self.env.cr.execute(f"""UPDATE {table_name} SET {many2one_name} = %s where id=%s
                """, (many2one_value, rec_id))

    def init(self):

        self.env.cr.execute("""
        UPDATE res_partner set write_date='2000-01-01' WHERE id<=6;
        UPDATE res_users set write_date='2000-01-01' WHERE id<=5;
        """)

        language = self.env['res.lang'].search([('code', '=', 'ar_001')])

        if not language:
            # If the language is not found, install it
            self.env['res.lang'].load_lang('ar_001')

        # Activate the language
        language.write({'active': True})

    def add_res_company_rel_for_all_users(self):
        cr = self.env.cr
        users = self.env['res.users'].sudo().with_context(active_test=False).search([])
        cr.execute("select user_id from res_company_users_rel")

        already_added_ids = {row[0] for row in cr.fetchall()}
        for user in users:
            if user.id not in already_added_ids:
                try:
                    cr.execute(f"""
                    insert into res_company_users_rel(cid,user_id)
                    VALUES (1,{user.id}) 
                    """)
                except Exception as ex:
                    _logger.warning(f'already created for this user{user.id}')

        # self.env['res.company'].sudo().write({'user_ids': [(6, 0, users.ids)]})

        # self.env['res.company'].sudo().user_ids = users
        cr.commit()

    @staticmethod
    def _get_encrypted_password(pool, user_id):
        try:
            if user_id <= 6:
                return
            model, uid, db, password = pool.get_connection()
            encrypted_password = model.execute_kw(
                db, uid, password,
                'res.users', 'get_encrypted_password',
                [user_id, config.get('xmlrpc_pass')]
            )
            return encrypted_password
        except Exception as ex:
            raise UserError(repr(ex))

    def get_matching_xml_gid_list(self, pool):
        model, uid, db, password = pool.get_connection()
        groups_id = self.env['res.groups'].search([]).ids

        xml_ids = self.env['ir.model.data'].search([
            ('res_id', 'in', groups_id),
            ('model', '=', 'res.groups'),
        ])
        domain = []
        for group in xml_ids:
            domain = expression.OR([
                domain,
                [['module', '=', group.module], ['name', '=', group.name]]]
            )

        # get updates_count
        group_xml_ids = model.execute_kw(
            db, uid, password, 'ir.model.data', 'search_read',
            [domain],
            {
                'fields': ['module', 'name', 'res_id'],
                'order': 'write_date, id',
                'context': {'active_test': False}  # Include non-active records
            }
        )

        return group_xml_ids
