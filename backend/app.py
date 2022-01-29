# main entrypoint for backend REST api
import yaml
import logging
import logging.config
import requests
import connexion
from datetime import datetime

from flask_cors import CORS, cross_origin

app_conf_file = "app_conf.yml"
log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s"% app_conf_file)
logger.info("Log Conf File: %s"% log_conf_file)

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path="/", strict_validation=True, validate_responses=True)
if "TARGET_ENV" not in os.environ or os.environ['TARGET_ENV'] != 'test':
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == '__main__':
    init_scheduler()
    app.run(port=8100, use_reloader=False, debug=False)