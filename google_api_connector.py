#!/usr/bin/env python
# -*- coding: utf8 -*-
import json
import os
import sys
import traceback

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


# Setup the Sheets API
# Checks for credentials.json to set a connection to Google API,
# if doesn't exsists tries to create a new one with de data available in client_secret.json
def connect_to_google_api():
    print("Connecting to google sheets...")
    scopes = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', scopes)
        creds = tools.run_flow(flow, store)
    google_api = build('sheets', 'v4', http=creds.authorize(Http()))
    print("Connection successful")
    return google_api


#  Spreadsheets IDS
#  USERS TABLE
# | uid_hashed | status | name | email | telegram_name |
users_spreadsheet_id = '1tpHH2elJiTqIe3Dav4Hzjqab3Rs137OjOKd9W0oNxr8'

#  LOG TABLE
# | Timestamp | uid_hashed | username | action |
log_spreadsheet_id = '1ISaxhpRb2POD-7LvGGSdrpCnZQmTw-p17DOtXoRZKNg'


# get_users_json connects to the Google Spreadsheets API
# and appends a new user.
# RETURNS True on success
def insert_user(uid_hashed, status="NONE", name="NONE", email="NONE", phone="NONE", telegram_name="NONE"):
    google_api = connect_to_google_api()
    try:
        data = [[uid_hashed, status, name, email, phone, telegram_name]]
        resource = {
            "majorDimension": "ROWS",
            "values": data
        }
        sheet_range = "usuarios!A1:F"
        google_api.spreadsheets().values().append(
            spreadsheetId=users_spreadsheet_id,
            range=sheet_range,
            body=resource,
            valueInputOption="RAW"
        ).execute()
        return True
    except:
        print("ERROR Al insertar usuario\nDetalles: " + traceback.format_exc())
        return False


# get_users_json connects to the Google Spreadsheets API
# and claims the list of users and their data,
# then generates a json file and returns the resulting dictionary
def get_users_json():
    google_api = connect_to_google_api()
    users_data = {}
    result = google_api.spreadsheets().values().get(
        spreadsheetId=users_spreadsheet_id,
        range="usuarios!A2:F"
    ).execute()
    for user in result["values"]:
        uid_hashed = user[0]
        status = user[1]
        name = user[2]
        email = user[3]
        phone = user[4]
        telegram_user = user[5]
        users_data[uid_hashed] = {
            'status': status,
            'name': name,
            'email': email,
            'phone': phone,
            'telegram_user': telegram_user,
        }
    with open('users.json', 'w') as outfile:
        json.dump(users_data, outfile)
    return users_data


# save_log connects to the Google Spreadsheets API
# and appends the log spreadsheet
# RETURNS True on success
def save_log():
    google_api = connect_to_google_api()
    try:
        with open('log.json') as log_json_file:
            log_data = json.load(log_json_file)
            data = []
            for timestamp in log_data:
                data.append([timestamp,
                             log_data.get(timestamp)["uid_hashed"],
                             log_data.get(timestamp)["username"],
                             log_data.get(timestamp)["action"]
                             ])
            resource = {
                "majorDimension": "ROWS",
                "values": data
            }
            sheet_range = "log!A:D"
            google_api.spreadsheets().values().append(
                spreadsheetId=log_spreadsheet_id,
                range=sheet_range,
                body=resource,
                valueInputOption="RAW"
            ).execute()
        os.remove('log.json')
        return True
    except IOError:
        print("Ninguna actividad que guardar")
    except:
        print("ERROR Al actualizar el log online\nDetalles: " + traceback.format_exc())
        return False


if __name__ == '__main__':
    if "--update_log" in sys.argv:
        save_log()
