import subprocess

service_name = 'odoo-server-15.0'

if __name__ == '__main__':
    subprocess.run(f'sc restart {service_name}', shell=True, check=True)
