#!/usr/bin/env python

import sys
import json
import yaml

data = json.loads(sys.stdin.read())

datapoints_gv_raw = data["graphicalViews"][0]["viewComponents"]
datapoints_gv = {
  datapoint["dataPointXid"]: {
    "id": datapoint["dataPointXid"],
    "script": datapoint["script"],
    "x": datapoint["x"],
    "y": datapoint["y"],
} for datapoint in datapoints_gv_raw}


datapoints = {
  datapoint["xid"]: {
    "id": datapoint["xid"],
    "name": datapoint["name"],
    "modbusDataType": datapoint["pointLocator"]["modbusDataType"],
    "offset": datapoint["pointLocator"]["offset"],
    "bit": datapoint["pointLocator"]["bit"],
    "dataSourceXid": datapoint["dataSourceXid"],
} for datapoint in data["dataPoints"]}

for dp_id in datapoints:
  datapoints[dp_id].update(datapoints_gv[dp_id])


datapoints_out = {"hmi_datapoints": list(datapoints.values())}

print(yaml.dump(datapoints_out, sort_keys=False))

datasources = {
  datasource["xid"]: {
    "id": datasource["xid"],
    "name": datasource["name"]
} for datasource in data["dataSources"]}


datasources_out = {"hmi_datasources": list(datasources.values())}

print(yaml.dump(datasources_out, sort_keys=False))
