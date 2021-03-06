# prometheus-jsonpath-exporter

Converts json data from a http url into prometheus metrics using jsonpath


### Config
 
#### For single JSON Endpoint

This syntax is implemented that the old configuration from previous versions do not break.

```yml
exporter_port: 9158 # Port on which prometheus can call this exporter to get metrics
log_level: info
json_data_url: http://stubonweb.herokuapp.com/kong-cluster-status # Url to get json data used for fetching metric values
metric_name_prefix: kong_cluster # All metric names will be prefixed with this value
metrics:
  - name: total_nodes # Final metric name will be kong_cluster_total_nodes
    description: Total number of nodes in kong cluster
    path: $.total
  - name: alive_nodes # Final metric name will be kong_cluster_alive_nodes
    description: Number of live nodes in kong cluster
    path: count($.data[@.status is "alive"])
```

#### For multiple JSON Endpoints

```yml
exporter_port: 9158 # Port on which prometheus can call this exporter to get metrics
log_level: info
endpoints: # you can define multiple endpoints even when they return different structures
  - json_data_url: http://stubonweb.herokuapp.com/kong-cluster-status # Url to get json data used for fetching metric values
    metric_name_prefix: kong_cluster_single # All metric names will be prefixed with this value
    metrics:
      - name: total_nodes # Final metric name will be kong_cluster_total_nodes
        description: Total number of nodes in kong cluster
        path: $.total
      - name: alive_nodes # Final metric name will be kong_cluster_alive_nodes
        description: Number of live nodes in kong cluster
        path: count($.data[@.status is "alive"])
  - json_data_urls: # OPTIONAL list to configure multiple data URLs separated by tag-label
      - url: http://stubonweb.herokuapp.com/kong-cluster-status # Url to get json data used for fetching metric values
        label: kong_cluster_1 # label value for label "tag"
      - url: http://stubonweb.herokuapp.com/kong-cluster-status # Url to get json data used for fetching metric values
        label: kong_cluster_2 # label value for label "tag"
    metric_name_prefix: kong_cluster_multiple # All metric names will be prefixed with this value
    metrics:
      - name: total_nodes # Final metric name will be kong_cluster_total_nodes
        description: Total number of nodes in kong cluster
        path: $.total
      - name: alive_nodes # Final metric name will be kong_cluster_alive_nodes
        description: Number of live nodes in kong cluster
        path: count($.data[@.status is "alive"])
```

See the example below to understand how the json data and metrics will look for this config

### Run

#### Using code (local)

```
# Ensure python 3.x and pip installed
pip install -r app/requirements.txt
python app/exporter.py example/config.yml
```

#### Using docker

```
docker run -p 9158:9158 -v $(pwd)/example/config.yml:/etc/prometheus-jsonpath-exporter/config.yml sunbird/prometheus-jsonpath-exporter /etc/prometheus-jsonpath-exporter/config.yml
```

### JsonPath Syntax

This exporter uses [objectpath](http://objectpath.org) python library. The syntax is documented [here](http://objectpath.org/reference.html)

### Example

For the above config, if the configured `json_data_url` returns

```json
{
  "data": [
    {
      "address": "x.x.x.15:7946",
      "status": "failed"
    },
    {
      "address": "x.x.x.19:7946",
      "status": "alive"
    },
    {
      "address": "x.x.x.12:7946",
      "status": "alive"
    }
  ],
  "total": 3
}
```

Metrics will available in http://localhost:9158



```
$ curl -s localhost:9158 | grep ^kong
kong_cluster_total_nodes 3.0
kong_cluster_alive_nodes 2.0
```

