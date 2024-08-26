# -*- coding: utf-8 -*-
from time import sleep
from xmlrpc import client
import logging
import ssl
from odoo.exceptions import UserError
from odoo import _

_logger = logging.getLogger(__name__)


class OdooConnectionPool:
    _instance = None
    _model = None
    _uid = None
    _db = None
    _password = None
    _srv = None
    _user = None
    _db_name = None
    _password_param = None

    def __new__(cls, env):
        if cls._instance is None:
            cls._instance = super(OdooConnectionPool, cls).__new__(cls)
            cls._instance._setup_connection_params(env)
            _logger.info('Created new instance of OdooConnectionPool.')
        else:
            _logger.info('Instance already exists. Checking connection.')
            if not cls._instance.check_connection():
                _logger.warning('Connection is invalid. Creating a new instance.')
                cls._instance = super(OdooConnectionPool, cls).__new__(cls)
                cls._instance._setup_connection_params(env)
                cls._instance.connect_to_server()
        return cls._instance

    def _setup_connection_params(self, env):
        """Set up connection parameters only once."""
        conf_mo = env['ir.config_parameter'].sudo()
        self._srv = conf_mo.get_param('server_address')
        self._user = conf_mo.get_param('server_user')
        self._db_name = conf_mo.get_param('server_db')
        self._password_param = conf_mo.get_param('server_password')

        # Initialize connection
        self.connect_to_server()

    def connect_to_server(self):
        for i in range(3):
            try:
                common = client.ServerProxy(f"{self._srv}/xmlrpc/2/common")
                uid = common.authenticate(self._db_name, self._user, self._password_param, {})
                model = client.ServerProxy(f"{self._srv}/xmlrpc/2/object", allow_none=True)

                if uid:
                    _logger.info("Connected to the server successfully.")
                    self._model = model
                    self._uid = uid
                    self._db = self._db_name
                    self._password = self._password_param
                    break
                else:
                    msg = "Authentication failed. Exiting ..."
                    _logger.warning(msg)
                    raise UserError(_(msg))
            except Exception as e:
                _logger.error(f"Connection failed: {e}. Retrying in 5 seconds...")
                sleep(5)  # Wait for 5 seconds before retrying
        else:
            raise UserError(_("Connection Failed, Check Your Connection"))

    def check_connection(self):
        """Check if the current connection is still valid by querying a small model like res.partner."""
        try:
            if self._model:  # Ensure _model is not None
                # Query a small model to validate the connection
                result = self._model.execute_kw(self._db, self._uid, self._password, 'res.partner', 'search', [[]], {})
                if isinstance(result, list):
                    _logger.info("Connection to the server is valid. Successfully queried 'res.partner'.")
                    return True
                else:
                    _logger.warning("Connection to the server is not valid.")
                    return False
            else:
                _logger.warning("No model available for querying.")
                return False
        except (ssl.SSLEOFError, ConnectionError) as e:
            _logger.error(f"Connection validation failed: {e}")
            return False
        except Exception as e:
            _logger.error(f"Connection validation failed: {e}")
            return False

    def get_connection(self):
        """Return connection details if the connection is valid. Attempt to reconnect if not."""
        if not self.check_connection():
            _logger.warning("Invalid connection detected. Attempting to reconnect...")
            self.connect_to_server()

            # Recheck the connection after attempting to reconnect
            if not self.check_connection():
                _logger.error("Reconnection attempt failed.")
                raise UserError(_("Reconnection attempt failed."))

        return self._model, self._uid, self._db, self._password
