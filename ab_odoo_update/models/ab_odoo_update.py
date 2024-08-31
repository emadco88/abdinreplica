import os
import subprocess
import time  # Import the time module for adding a delay
from odoo import models, api, tools
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class OdooServerControl(models.AbstractModel):
    _name = 'ab_odoo_update'

    @api.model
    def git_pull(self):
        # Step 1: Use tools.config to get the addons_path from the current Odoo configuration
        addons_path = tools.config['addons_path']

        # Assuming the odoo_replica_addons is one of the directories in addons_path
        replica_addons_path = None
        for path in addons_path.split(','):
            if 'replica_addons' in path:
                replica_addons_path = path.strip()
                break

        if not replica_addons_path:
            raise UserError('odoo_replica_addons path not found in addons_path')

        # Step 2: Perform a git pull on the replica_addons repository
        os.chdir(replica_addons_path)
        subprocess.run(['git', 'pull'], check=True)

    @api.model
    def restart_odoo_service(self):
        try:
            # Step 1: Get the script path from addons_path
            script_path = ''
            addons_path = tools.config['addons_path']
            for path in addons_path.split(','):
                if 'replica_addons' in path:
                    script_path = path.strip()
                    break

            # Construct the path to the Python executable
            python_path = os.path.join(script_path, '..', 'python', 'python.exe')

            # Construct the path to the external script
            script_path = os.path.join(script_path, 'ab_odoo_update', 'restart_odoo_server.py')

            _logger.info(f'Constructed script path: {script_path}')

            # Ensure the script exists
            if not os.path.isfile(script_path):
                raise Exception(f"Script not found: {script_path}")

            _logger.info(f'Python executable path:\n {python_path}')
            _logger.info(f'Script path:\n {script_path}')

            # Replace backslashes with double backslashes for Windows compatibility
            python_path = python_path.replace('\\', '\\\\')
            script_path = script_path.replace('\\', '\\\\')

            subprocess.run([python_path, script_path], check=True)
            _logger.info('Restart command issued successfully.')

            return {'status': 'success', 'message': 'Restart command issued successfully.'}
        except Exception as e:
            _logger.error(f'Error restarting Odoo server: {str(e)}')
            return {'status': 'error', 'message': str(e)}
