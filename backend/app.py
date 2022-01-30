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
    print(duration)
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
    print(f'converted duration: {duration}')
    return datetime.fromtimestamp((datetime.timestamp(end_time) - duration))

def get_traceroutes(src, dest, search_duration, end_time, num_tracert):
    """ Retrieves array of traceroutes from Prometheus """
    logger.info(f'Getting traceroutes')

    traceroutes = []
    hops = []

    end_time = parse_datetime(end_time)
    start_time = process_duration(search_duration, end_time)
    interval_seconds = ((end_time - start_time).seconds / num_tracert)
    # print('start time:')
    # print(start_time)
    # print('end time:')
    # print(end_time)


    instance = src
    target = dest


    # TODO:
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

    traceroutes_metric_list_data = MetricsList(tracert_metric_range_data) # metric_object_list will be initialized as
                                                # a list of Metric objects for all the
                                                # metrics downloaded using get_metric query

    # We can see what each of the metric objects look like
    # for item in traceroutes_metric_list_data:
    #     print(item, "\n")
    #     hops += [{'ttl': int(item.label_config['ttl']), 'host': item.label_config['path'], 'trace_time': '2016-08-29T09:12:33.001Z'}]

    # tracert_df = MetricRangeDataFrame(tracert_metric_range_data)
    # print('traceroute:')
    # print(tracert_df.head())
    # print(tracert_df.index)

    # print('rows at timestamp 1643511196.308')
    # print(tracert_df.loc[1643511196.308])

    # current_ts = tracert_df.index.max()
    # for i in range(num_tracert):
    #     print(tracert_df.loc[current_ts])
    #     current_ts = current_ts - interval_seconds

    # Parse TTLs into something we can make sense of for each traceroute on the graph
    # print(traceroutes)

    return traceroutes, 200

if __name__ == '__main__':
    startup()