# main entrypoint for backend REST api
import yaml
import logging
import logging.config
import requests
import connexion
from datetime import datetime
from prometheus_api_client import PrometheusConnect, PrometheusApiClientException
from flask_cors import CORS, cross_origin

# set up logging and app configuration
app_conf_file = "app_conf.yml"
log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

def startup():
    """ Connects to Prometheus TSDB and starts Flask App """
    connect_prometheus()
    app = connexion.FlaskApp(__name__, specification_dir='')
    app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

    logger.info(f"Backend running on localhost:{app_config['app']['port']}")
    logger.info(f"Make requests at http://localhost:{app_config['app']['port']}/ui")
    
    app.run(port=app_config['app']['port'], use_reloader=False, debug=False)

def connect_prometheus():
    """ Attempts connection with Prometheus """
    global prom
    logger.info(f"Attempting to connect to Prometheus at http://{app_config['prometheus']['host']}...")
    try:
        prom = PrometheusConnect(url=f"http://{app_config['prometheus']['host']}", disable_ssl=True)
    except Error as e:
        logger.info(f"Failed to connect to Prometheus at http://{app_config['prometheus']['host']}. Please check your connection details and try again. Error:")
        logger.info(e)
        exit(1)
    logger.info(f"Connection to Prometheus succeeded.")

def get_traceroutes(body):
    """ Retrieves array of traceroutes from Prometheus """
    logger.info(f'Getting traceroutes')

    return traceroutes, 200

if __name__ == '__main__':
    startup()