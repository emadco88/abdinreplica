import subprocess

service_name = 'odoo-server-15.0'


def stop_odoo_service():
    """Stop the Odoo service."""
    subprocess.run(f'sc stop {service_name}', shell=True, check=True)


if __name__ == '__main__':
    stop_odoo_service()
