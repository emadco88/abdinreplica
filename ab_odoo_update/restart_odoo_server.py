import subprocess

service_name = 'odoo-server-15.0'

if __name__ == '__main__':
    subprocess.run(f'net stop odoo-server-15.0  && net start odoo-server-15.0', shell=True, check=True)
