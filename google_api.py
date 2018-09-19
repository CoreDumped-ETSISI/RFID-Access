#! python3
import logging
from oauth2client import file, client, tools
from apiclient.discovery import build
from httplib2 import Http
from time import time

logger = logging.getLogger("GoogleAPI")
logger.setLevel(logging.DEBUG)

# | hashedUid | status | name | email | telegram_name |
USERS_SS_ID = "1tpHH2elJiTqIe3Dav4Hzjqab3Rs137OjOKd9W0oNxr8"
# | Timestamp | hashedUid | username | action |
LOG_SS_ID = "1ISaxhpRb2POD-7LvGGSdrpCnZQmTw-p17DOtXoRZKNg"
LAST = [0]


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


def get_users():
    if LAST[-1] + 1800 > time():
        raise Exception("Half an hour limit")
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
    LAST.append(time())
    return userData
