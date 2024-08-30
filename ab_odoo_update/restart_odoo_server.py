import os
import subprocess
import time
import re


def restart_odoo_service():
    try:
        service_name = 'odoo-server-15.0'

        # Stop the Odoo service
        subprocess.run(f'sc stop {service_name}', shell=True, check=True)

        # Wait for the service to fully stop
        for _ in range(10):  # Check the service status up to 10 times
            status_output = subprocess.check_output(f'sc query {service_name}', shell=True).decode()

            # Use regex to check for the STOPPED state
            if re.search(r'STATE\s+:\s+1\s+STOPPED', status_output):
                break  # Service has stopped
            time.sleep(1)  # Wait for 1 second before checking again
        else:
            raise Exception('Service did not stop in time.')

        # Start the Odoo service
        subprocess.run(f'sc start {service_name}', shell=True, check=True)

        print('Odoo server restarted successfully.')
    except subprocess.CalledProcessError as e:
        print(f'Failed to execute command: {e}')
    except Exception as e:
        print(f'Error: {str(e)}')


if __name__ == '__main__':
    restart_odoo_service()
