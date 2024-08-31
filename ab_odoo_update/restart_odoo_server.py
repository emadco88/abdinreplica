import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    filename='odoo_service_restart.log',  # Name of the log file
    filemode='a',  # Append mode; use 'w' for write mode if you want to overwrite
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    level=logging.INFO  # Set the minimum log level to INFO
)

_logger = logging.getLogger(__name__)

service_name = 'odoo-server-15.0'


def restart_odoo_service():
    try:
        _logger.info('Restarting Odoo service...')
        stop_odoo_service()
        _logger.info('Odoo service stopped successfully.')
        time.sleep(2)
        start_odoo_service()
        _logger.info('Odoo service started successfully.')
    except subprocess.CalledProcessError as e:
        _logger.error(f'Error restarting Odoo service: {e}')
        raise


def stop_odoo_service():
    try:
        _logger.info(f'Stopping Odoo service: {service_name}')
        return subprocess.run(f'sc stop {service_name}', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        _logger.error(f'Failed to stop Odoo service: {e}')
        raise


def start_odoo_service():
    try:
        _logger.info(f'Starting Odoo service: {service_name}')
        return subprocess.run(f'sc start {service_name}', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        _logger.error(f'Failed to start Odoo service: {e}')
        raise


if __name__ == '__main__':
    restart_odoo_service()
