import logging
from odoo import models, _
from odoo.exceptions import UserError
from .ping_host import ping
from contextlib import contextmanager
from cryptography.fernet import Fernet
from odoo.tools import config

SERVER = None


def _get_server():
    global SERVER
    if SERVER:
        return SERVER

    conf_bconnect_ips = [config.get('bconnect_ip1'), config.get('bconnect_ip2'), ]
    if not conf_bconnect_ips:
        raise UserError(_("NO IPs in odoo config file."))

    for value in conf_bconnect_ips:
        _logger.info(f"######## Trying IP {value} #########")
        if ping(value):
            SERVER = value
            return SERVER
    raise UserError(_("All BConnect Server IPs may be Offline."))


USER = config.get('bconnect_user')
DB = config.get('bconnect_db')
DECRYPTION_KEY = config.get('decryption_key')

_logger = logging.getLogger(__name__)


class EPlusConnect(models.AbstractModel):
    _name = 'ab_eplus_connect'
    _description = 'ab_eplus_connect'

    # Connection pool to store connections by user
    _connection_pool = {}

    def decrypt_password(self):
        encrypted_password = bytes(self.env['ir.config_parameter'].sudo().get_param("bconnect_crypt_pass"), 'utf-8')
        cipher = Fernet(bytes(DECRYPTION_KEY, 'utf-8'))
        password = cipher.decrypt(encrypted_password).decode('utf-8')
        return password

    def is_connection_valid(self, conn):
        """Check if the connection is still valid."""
        try:
            # Perform a simple query to check if the connection is alive
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            return True
        except Exception as ex:
            _logger.error(f"Connection validation error: {ex}")
            return False

    @contextmanager
    def connect_eplus(self, server='',
                      db=DB, user=USER, password=None,
                      param_str='%s',
                      charset='CP1256',
                      autocommit=True):

        server = server or _get_server()

        user_id = (self.env.uid, server, param_str)
        if user_id in self._connection_pool:
            conn = self._connection_pool.get(user_id)
            if not self.is_connection_valid(conn):
                _logger.info(f"Connection for user {user_id} is no longer valid. Creating a new connection.")
                self._connection_pool.pop(user_id, None)
            else:
                _logger.info(f"Using Current Connection for user {user_id}.")

        if user_id not in self._connection_pool:
            password = password or self.decrypt_password()
            _logger.info(f"Creating New Connection For {user_id} ...")

            if param_str == '?':
                import pyodbc
                sqldrivers = [sqldriver for sqldriver in pyodbc.drivers() if 'SQL Server' in sqldriver]
                if sqldrivers:
                    conn = pyodbc.connect(
                        f'Driver={sqldrivers[-1]};'
                        f'Server={server};'
                        f'Database={db};'
                        'Port=1433;'
                        'TrustServerCertificate=yes;'
                        f'UID={user};'
                        f'PWD={password}',
                        autocommit=autocommit)
                else:
                    raise UserError(_("No ODBC Driver for SQL Server available, Please Contact dev team."))
            else:
                import pymssql
                conn = pymssql.connect(
                    server=server,
                    user=user,
                    password=password,
                    database=db,
                    timeout=0,
                    appname=None,
                    login_timeout=10,
                    charset=charset,
                    autocommit=autocommit)

            self._connection_pool[user_id] = conn

        # Use the existing connection
        conn = self._connection_pool[user_id]

        try:
            yield conn
        except Exception as ex:
            _logger.error(repr(ex))

        finally:
            # conn.close()
            # Optionally close the connection if needed (e.g., on logout)
            pass
