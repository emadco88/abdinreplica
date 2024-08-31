import subprocess
import time
import re

service_name = 'odoo-server-15.0'


def is_service_stopped():
    """Check if the Odoo service is stopped."""
    result = subprocess.run(f'sc query {service_name}', shell=True, capture_output=True, text=True)

    # Use regex to check the service state
    return re.search(r'STATE\s*:\s*1\s*STOPPED', result.stdout) is not None


def start_odoo_service():
    """Start the Odoo service."""
    subprocess.run(f'sc start {service_name}', shell=True, check=True)


if __name__ == '__main__':
    # Run stop_odoo_service in a separate Python instance
    # subprocess.run(['D:\\odoo\\python\\python.exe', 'stop_service.py'], check=True)
    subprocess.run(f'sc stop {service_name}', shell=True, check=True)
    # Wait until the service is stopped
    for _ in range(5):
        if not is_service_stopped():
            time.sleep(1)  # Check every second
        else:
            break

    start_odoo_service()
