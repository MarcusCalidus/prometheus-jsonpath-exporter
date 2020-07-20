#!/usr/bin/python

import argparse
import json
import logging
import time
from urllib.request import urlopen
import yaml
from objectpath import Tree
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

DEFAULT_PORT = 9158
DEFAULT_LOG_LEVEL = 'info'


class JsonPathCollector(object):
    def __init__(self, config):
        self._config = config

    def collect(self):
        config = self._config
        if 'endpoints' in config:
            endpoint_list = config['endpoints']
        else:
            endpoint_list = [config]

        for endpoint_config in endpoint_list:
            if 'json_data_url' in endpoint_config:
                single_data = {"url": endpoint_config['json_data_url']}
                data_url_list = [single_data]
            else:
                data_url_list = endpoint_config['json_data_urls']

            for data_url in data_url_list:
                result = json.loads(urlopen(data_url['url'], timeout=10).read())
                result_tree = Tree(result)
                for metric_config in endpoint_config['metrics']:
                    metric_name = "{}_{}".format(endpoint_config['metric_name_prefix'], metric_config['name'])
                    metric_description = metric_config.get('description', '')
                    metric_path = metric_config['path']
                    value = result_tree.execute(metric_path)
                    if "label" in data_url:
                        logging.debug("metric_name: {}, tag: {}, value for '{}' : {}".format(metric_name, data_url["label"], metric_path, value))
                        metric = GaugeMetricFamily(metric_name, metric_description, labels=['tag'])
                        metric.add_metric(labels=[data_url["label"]], value=value)
                    else:
                        logging.debug("metric_name: {}, value for '{}' : {}".format(metric_name, metric_path, value))
                        metric = GaugeMetricFamily(metric_name, metric_description, value=value)
                    yield metric


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Expose metrics bu jsonpath for configured url')
    parser.add_argument('config_file_path', help='Path of the config file')
    args = parser.parse_args()
    with open(args.config_file_path) as config_file:
        config = yaml.load(config_file)
        log_level = config.get('log_level', DEFAULT_LOG_LEVEL)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.getLevelName(log_level.upper()))
        exporter_port = config.get('exporter_port', DEFAULT_PORT)
        logging.debug("Config %s", config)
        logging.info('Starting server on port %s', exporter_port)
        start_http_server(exporter_port)
        REGISTRY.register(JsonPathCollector(config))
    while True: time.sleep(1)
