# -*- coding: utf-8 -*-
from time import sleep
from xmlrpc import client
import logging

_logger = logging.getLogger(__name__)


class OdooConnectionPool:
    _instance = None
    _model = None
    _uid = None
    _db = None
    _password = None

    def __new__(cls, env):
        if cls._instance is None:
            cls._instance = super(OdooConnectionPool, cls).__new__(cls)
        return cls._instance

    def __init__(self, env):
        self.env = env
        if self._model is None or self._uid is None:
            self.connect_to_server()

    def connect_to_server(self):
        conf_mo = self.env['ir.config_parameter'].sudo()
        while True:
            try:
                # Get Replication Auth
                srv = conf_mo.get_param('server_address')
                user = conf_mo.get_param('server_user')
                db = conf_mo.get_param('server_db')
                password = conf_mo.get_param('server_password')

                common = client.ServerProxy(f"{srv}/xmlrpc/2/common")
                uid = common.authenticate(db, user, password, {})
                model = client.ServerProxy(f"{srv}/xmlrpc/2/object", allow_none=True)

                if uid:
                    _logger.info("Connected to the server successfully.")
                    self._model = model
                    self._uid = uid
                    self._db = db
                    self._password = password
                    break
                else:
                    _logger.warning("Authentication failed. Exiting ...")
                    break
            except Exception as e:
                _logger.error(f"Connection failed: {e}. Retrying in 30 seconds...")

            sleep(30)  # Wait for 5 seconds before retrying

    def get_connection(self):
        return self._model, self._uid, self._db, self._password
