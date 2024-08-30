import os
import subprocess
import time  # Import the time module for adding a delay
from odoo import models, api, tools


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
            # Path to the .bat file or its shortcut
            bat_file_path = os.path.join(tools.config['addons_path'], 'ab_odoo_update', 'restart_odoo_server')

            # Ensure the .bat file exists
            if not os.path.isfile(bat_file_path):
                raise Exception(f"Batch file not found: {bat_file_path}")

            # Run the .bat file (admin privileges should be handled by the shortcut)
            subprocess.Popen([bat_file_path], shell=True)

            return {'status': 'success', 'message': 'Restart command issued successfully.'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
