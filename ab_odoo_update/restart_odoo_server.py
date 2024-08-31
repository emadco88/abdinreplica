import subprocess
import time


def restart_odoo_service():
    service_name = 'odoo-server-15.0'

    # Stop the Odoo service
    subprocess.run(f'sc stop {service_name}', shell=True, check=True)
    time.sleep(2)  # Wait for 1 second before checking again
    subprocess.run(f'sc start {service_name}', shell=True, check=True)


if __name__ == '__main__':
    restart_odoo_service()
