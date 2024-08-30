import os
import subprocess
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
            # Step 3: Restart the Odoo server
            if os.name == 'nt':  # For Windows
                # Restart the Odoo service using the correct service name
                command = 'net stop odoo-server-15.0 && net start odoo-server-15.0'
            else:  # For Linux/Unix
                # Example command for restarting Odoo on Linux
                command = 'sudo systemctl restart odoo15'

            subprocess.run(command, shell=True, check=True)

            return {'status': 'success', 'message': 'Odoo server restarted successfully.'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
