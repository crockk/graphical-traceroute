# main entrypoint for backend REST api
import yaml
import logging
import logging.config
import requests
import connexion
import re
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

# define global variables
try:
    MAX_ROUTES = int(app_config['app']['max_routes'])
    LISTEN_PORT = int(app_config['app']['port'])
    PROMETHEUS_HOST = app_config['prometheus']['host']
except KeyError as e:
    msg = 'Required app configuration value not found in app_conf.yml.'
    logger.error(f'{msg} Error:')
    logger.error(e)
    exit(1)

# connect to prometheus
logger.info(f"Attempting to connect to Prometheus at http://{PROMETHEUS_HOST}...")
try:
    prom = PrometheusConnect(url=f"http://{PROMETHEUS_HOST}", disable_ssl=True)
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

    logger.info(f"Backend running on localhost:{LISTEN_PORT}")
    logger.info(f"Make requests at http://localhost:{LISTEN_PORT}/ui")
    
    app.run(port=LISTEN_PORT, use_reloader=True, debug=False)

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
    # else:
    #     raise ValueError(f"Time unit '{duration[-1]}' is not supported. The following units are supported: s, m, h, d")
    return datetime.fromtimestamp((datetime.timestamp(end_time) - duration))


def max_routes():
    """ Obtains max_routes from backend application configuration """
    return { 'max_routes': MAX_ROUTES } , 200

def validate_params(src, dest, num_tracert, duration, end_time):
    """ Validates query parameters src, dest, and num_tracert """
    msg = 'An unknown error occurred.'
    if num_tracert > MAX_ROUTES:
        msg = f'Number of traceroutes requested ({num_tracert}) exceeds MAX_ROUTES configuration value ({MAX_ROUTES})'
        logger.error(f'{msg}')
        raise ValueError(msg)
    elif num_tracert <= 0:
        msg = f'Number of traceroutes requested ({num_tracert}) must be greater than 0.'
        logger.error(f'{msg}')
        raise ValueError(msg)

    duration_re_str = '^[0-9]*[1-9][0-9]*(s|m|h|d)$'
    duration_re = re.compile(duration_re_str)
    if not duration_re.match(duration):
        msg = f"Search duration time unit '{duration[-1]}' is not supported. The following units are supported: s, m, h, d"
        logger.error(f'{msg}')
        raise ValueError(msg)

    end_re_str = '^(now|([0-9]*[1-9][0-9]*(s|m|h|d)))$'
    end_re = re.compile(end_re_str)
    if not end_re.match(end_time):
        msg = f"End time format '{end_time}' is not supported. The following time units are supported: s, m, h, d, or specify the current time with the keyword 'now'"
        logger.error(f'{msg}')
        raise ValueError(msg)

def get_traceroutes(src, dest, search_duration, end_time, num_tracert):
    """ Retrieves array of traceroutes from Prometheus """
    logger.info(f'Getting traceroutes')

    try:
        validate_params(src, dest, num_tracert, search_duration, end_time)
    except ValueError as e:
        return {'msg': str(e)}, 400

    # Use query params to get metrics
    tracert_metric_range_data, interval_seconds, start_time, end_time = generate_metric_range_data(src, dest, search_duration, end_time, num_tracert)
        
    # Generate traceroutes from metric range data
    try:
        traceroutes = generate_traceroutes(tracert_metric_range_data, num_tracert, start_time, end_time, interval_seconds)
    except KeyError as e:
        return {'msg': str(e)}, 404
    return traceroutes, 200

def generate_metric_range_data(src, dest, search_duration, end_time, num_tracert):
    """ Parses query params and returns metric range data from Prometheus """

    end_time = parse_datetime(end_time)
    start_time = process_duration(search_duration, end_time)
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

    return tracert_metric_range_data, interval_seconds, start_time, end_time

def generate_traceroutes(tracert_metric_range_data, num_tracert, start_time, end_time, interval_seconds):
    """ Generate traceroutes from metric range data"""
    try:
        tracert_df = MetricRangeDataFrame(tracert_metric_range_data)
    except KeyError as e:
        msg = f'No metrics found within the specified range ({start_time} - {end_time}). Please try widening the range.'
        logger.error(f'{msg}')
        raise KeyError(msg)

    this_timestamp = tracert_df.index.max()
    traceroutes = []
    for i in range(num_tracert):
        hops = []
        try:
            hop_vals = tracert_df.loc[this_timestamp, ["path", "ttl"]].values
        except KeyError as e:
            msg = f'No metrics found within the specified range ({start_time} - {end_time}). Please try widening the range.'
            logger.error(f'{msg}')
            raise KeyError(msg)
        for hop in hop_vals:
            this_hop = {}
            this_hop['host'] = hop[0]
            this_hop['ttl'] = int(hop[1])
            hops.append(this_hop)
        traceroutes.append({'hops': hops, 'trace_time': datetime.fromtimestamp(this_timestamp)})
        this_timestamp = this_timestamp - interval_seconds
    return traceroutes

if __name__ == '__main__':
    startup()