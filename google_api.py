#! python3
import logging
from oauth2client import file, client, tools
from apiclient.discovery import build
from httplib2 import Http
from json import dump, load
from sys import argv
from os import remove

"""
insert_user(hashedUid, status, name, email, phone, telegramName)
get_users()
save_log()
"""

logger = logging.getLogger("GoogleAPI")
logger.setLevel(logging.DEBUG)

# | hashedUid | status | name | email | telegram_name |
USERS_SS_ID = "1tpHH2elJiTqIe3Dav4Hzjqab3Rs137OjOKd9W0oNxr8"
# | Timestamp | hashedUid | username | action |
LOG_SS_ID = "1ISaxhpRb2POD-7LvGGSdrpCnZQmTw-p17DOtXoRZKNg"


def _connect():
    """Connect to google spreadsheets API and return the object"""
    logger.info("Connecting to google sheets...")
    scopes = "https://www.googleapis.com/auth/spreadsheets"
    store = file.Storage("credentials.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("client_secret.json", scopes)
        creds = tools.run_flow(flow, store)
    googleApi = build("sheets", "v4", http=creds.authorize(Http()))
    logger.info("Connection successful")
    return googleApi


def insert_user(hashedUid, status, name, email, phone, telegramName):
    googleApi = _connect()
    try:
        resource = {
            "majorDimension": "ROWS",
            "values": [[hashedUid, status, name, email, phone, telegramName]]}
        googleApi.spreadsheets().values().append(
            spreadsheetId=USERS_SS_ID,
            range="usuarios!A1:F",
            body=resource,
            valueInputOption="RAW"
        ).execute()
        return True
    except Exception as e:
        logger.exception("Error al insertar usuario\n" + str(e))


def get_users():
    googleApi = _connect()
    userData = {}
    result = googleApi.spreadsheets().values().get(
        spreadsheetId=USERS_SS_ID,
        range="usuarios!A2:F"
    ).execute()
    for user in result["values"]:
        hashedUid, status, name, email, phone, telegramUser = user[:6]
        userData[hashedUid] = {
            "status": status,
            "name": name,
            "email": email,
            "phone": phone,
            "telegramUser": telegramUser}
    with open("users.json", "w") as f:
        dump(userData, f)
    return userData


def save_log():
    googleApi = _connect()
    try:
        with open("log.json") as f:
            logData = load(f)
            data = [[timestamp, j["hashedUid"], j["username"], j["action"]]
                    for timestamp, j in logData.items()]
            resource = {
                "majorDimension": "ROWS",
                "values": data}
            googleApi.spreadsheets().values().append(
                spreadsheetId=LOG_SS_ID,
                range="log!A:D",
                body=resource,
                valueInputOption="RAW"
            ).execute()
        remove("log.json")
    except FileNotFoundError as e:
        logger.exception("Ninguna actividad que guardar\n" + str(e))
    except Exception as e:
        logger.exception("Error al actualizar el log online\n" + str(e))


if __name__ == "__main__" and "--update_log" in argv:
    save_log()
