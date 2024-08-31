import subprocess
import time

service_name = 'odoo-server-15.0'


def stop_odoo_service():
    # Stop the Odoo service
    return subprocess.run(f'sc stop {service_name}', shell=True, check=True)


def start_odoo_service():
    # Stop the Odoo service
    return subprocess.run(f'sc start {service_name}', shell=True, check=True)


if __name__ == '__main__':
    stop_odoo_service()
    time.sleep(2)
    start_odoo_service()
