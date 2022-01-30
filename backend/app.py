# main entrypoint for backend REST api
import yaml
import logging
import logging.config
import requests
import connexion
import pandas as pd
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta

from prometheus_api_client import PrometheusConnect, PrometheusApiClientException, MetricsList, Metric, MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime

# set up logging and app configuration
app_conf_file = "app_conf.yml"
log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

# connect to prometheus
logger.info(f"Attempting to connect to Prometheus at http://{app_config['prometheus']['host']}...")
try:
    prom = PrometheusConnect(url=f"http://{app_config['prometheus']['host']}", disable_ssl=True)
except Error as e:
    logger.info(f"Failed to connect to Prometheus. Error:")
    logger.info(e)
    exit(1)
logger.info(f"Connection to Prometheus succeeded.")

def startup():
    """ Configures and starts Flask App """
    app = connexion.FlaskApp(__name__, specification_dir='')
    app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

    logger.info(f"Backend running on localhost:{app_config['app']['port']}")
    logger.info(f"Make requests at http://localhost:{app_config['app']['port']}/ui")
    
    app.run(port=app_config['app']['port'], use_reloader=True, debug=False)

def process_duration(duration, end_time):
    """ Gets date based on a given duration and end time"""
    if duration[-1] == 's':
        duration = int(duration[:-1])
    elif duration[-1] == 'm':
        duration = int(duration[:-1]) * 60
    elif duration[-1] == 'h':
        duration = int(duration[:-1]) * 3600
    elif duration[-1] == 'd':
        duration = int(duration[:-1]) * 86400
    else:
        raise ValueError(f"Time unit {duration[-1]} is not supported. The following units are supported: s, m, h, d")
    return datetime.fromtimestamp((datetime.timestamp(end_time) - duration))


def max_routes():
    return { 'max_routes': int(app_config['app']['max_routes']) } , 200

def get_traceroutes(src, dest, search_duration, end_time, num_tracert):
    """ Retrieves array of traceroutes from Prometheus """
    logger.info(f'Getting traceroutes')

    traceroutes = []

    end_time = parse_datetime(end_time)
    try:
        start_time = process_duration(search_duration, end_time)
    except ValueError as e:
        logger.error(f'An exception occured while processing the query parameter: {duration}. Error:')
        logger.error(e)
        return {}, 400
    interval_seconds = ((end_time - start_time).seconds / num_tracert)

    instance = src
    target = dest

    # Generate PromQL query from query params
    metric = 'mtr_rtt_seconds'
    label_config = {
        'instance': instance,
        'target': target, 
        'type': 'mean'
        }

    tracert_metric_range_data = prom.get_metric_range_data(
        metric_name=metric,
        label_config=label_config,
        start_time=start_time,
        end_time=end_time,
    )

    # Generate dataframe for data processing
    tracert_df = MetricRangeDataFrame(tracert_metric_range_data)

    this_timestamp = tracert_df.index.max()
    for i in range(num_tracert):
        hops = []
        hop_vals = tracert_df.loc[this_timestamp, ["path", "ttl"]].values
        for hop in hop_vals:
            this_hop = {}
            this_hop['host'] = hop[0]
            this_hop['ttl'] = int(hop[1])
            hops.append(this_hop)
        traceroutes.append({'hops': hops, 'trace_time': datetime.fromtimestamp(this_timestamp)})
        this_timestamp = this_timestamp - interval_seconds

    return traceroutes, 200

if __name__ == '__main__':
    startup()