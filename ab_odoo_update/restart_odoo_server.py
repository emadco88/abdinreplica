import subprocess

service_name = 'odoo-server-15.0'

if __name__ == '__main__':
    # subprocess.run(f'sc stop {service_name} && timeout /t 5 && sc start {service_name}', shell=True, check=True)

    batch_file_path = 'restart_odoo_server'
    subprocess.run(f'start "" "{batch_file_path}"', shell=True)
