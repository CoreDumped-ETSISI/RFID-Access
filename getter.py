#! python3
import logging
from oauth2client import file, client, tools
from apiclient.discovery import build
from httplib2 import Http
from time import time
from http.client import HTTPConnection
from json import load, dump

logger = logging.getLogger("Input")
logger.setLevel(logging.DEBUG)

# | hashedUid | status | name | email | telegram_name |
USERS_SS_ID = "1tpHH2elJiTqIe3Dav4Hzjqab3Rs137OjOKd9W0oNxr8"
DEFAULT_TIMEOUT = 3


def _check_connection(timeout):
    conn = HTTPConnection("www.google.com", timeout=timeout)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except Exception as e:
        logger.warn("Connection problem: \n" + str(e))
        conn.close()
        return False


def _google_connect():
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


def _load_json():
    try:
        with open("users.json") as f:
            local = load(f)
    except FileNotFoundError:
        logger.warn("Users was not found. Empty dict")
        local = {}
    return local


def _dump_json(data):
    logger.warn("Rewriting users.json")
    with open("users.json", "w") as f:
        dump(data, f)


class Getter():
    def __init__(self):
        self.lastTry = 0
        self.users = {}
        self.get_users()

    def get_users(self):
        if self.lastTry + 1800 < time():
            logger.info("Half an hour limit")
            return
        local = _load_json()
        self.users = local
        if _check_connection(DEFAULT_TIMEOUT):
            googleApi = _google_connect()
            result = googleApi.spreadsheets().values().get(
                    spreadsheetId=USERS_SS_ID,
                    range="usuarios!A2:F").execute()
            google = {}
            for user in result["values"]:
                google[user[0]] = {
                    "status": user[1],
                    "name": user[2],
                    "email": user[3],
                    "phone": user[4],
                    "telegramUser": user[5]}
            if google != local:
                _dump_json(google)
                self.users = google
        self.lastTry = time()
