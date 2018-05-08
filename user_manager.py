#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
from google_api_connector import insert_user


def read_users_file():
    with open('users.json') as log_json_file:
        return json.load(log_json_file)


def write_users_file(log_data):
    with open('users.json', 'w') as outfile:
        json.dump(log_data, outfile)


# new_log_entry creates a new entry in the user.json file
def new_user_entry(uid_hashed, status="NONE", name="NONE", email="NONE", phone="NONE", telegram_name="NONE"):
    users_data = read_users_file()
    users_data[uid_hashed] = {"status": status, "name": name, "email": email, "phone": phone,
                              "telegram_name": telegram_name, }
    insert_user(uid_hashed, status, name, email, phone, telegram_name)
    write_users_file(users_data)
