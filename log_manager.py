#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  LOG TABLE
# | Timestamp | uid_hashed | username | action |
import time
import datetime
import json


def read_json_file():
    with open('log.json') as log_json_file:
        return json.load(log_json_file)


def write_json_file(log_data):
    with open('log.json', 'w') as outfile:
        json.dump(log_data, outfile)


# new_log_entry creates a new entry in the log.json file
def new_log_entry(uid_hashed="xxx", username="unknown", action="not especified"):
    log_data = read_json_file()
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%d/%m/%Y %H:%M:%S')
    log_data[timestamp] = {"uid_hashed": uid_hashed, "username": username, "action": action}
    write_json_file(log_data)
