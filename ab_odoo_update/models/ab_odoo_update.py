import os
import subprocess
import time  # Import the time module for adding a delay
from odoo import models, api, tools
from odoo.exceptions import UserError


class OdooServerControl(models.AbstractModel):
    _name = 'ab_odoo_update'

    @api.model
    def git_pull(self):
        try:
            # Step 1: Use tools.config to get the addons_path from the current Odoo configuration
            addons_path = tools.config['addons_path']

            # Assuming the odoo_replica_addons is one of the directories in addons_path
            replica_addons_path = None
            for path in addons_path.split(','):
                if 'replica_addons' in path:
                    replica_addons_path = path.strip()
                    break

            if not replica_addons_path:
                raise Exception('odoo_replica_addons path not found in addons_path')

            # Step 2: Perform a git pull on the replica_addons repository
            os.chdir(replica_addons_path)
            subprocess.run(['git', 'pull'], check=True)

            return {'status': 'success', 'message': 'Git Pull new updates successfully.'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @api.model
    def restart_odoo_server(self):
        try:
            script_path = ''
            addons_path = tools.config['addons_path']
            for path in addons_path.split(','):
                if 'replica_addons' in path:
                    script_path = path.strip()
                    break

            # Step 1: Construct the path to the external script
            script_path = os.path.join(script_path, 'ab_odoo_update', 'restart_odoo_server.py')

            # Step 2: Ensure the script exists
            if not os.path.isfile(script_path):
                raise UserError(f"Script not found: {script_path}")

            # Step 3: Use runas to run the script as admin
            command = f'runas /user:Administrator "python {script_path}"'
            subprocess.Popen(command, shell=True)

            return {'status': 'success', 'message': 'Restart command issued successfully.'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
