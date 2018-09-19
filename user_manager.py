#! python3
import logging
from google_api import insert_user
from google_api import get_users
from json import load, dump

logger = logging.getLogger("Users")
logger.setLevel(logging.DEBUG)


def get_dict():
    # First load local
    try:
        with open("users.json") as f:
            local = load(f)
    except FileNotFoundError:
        logger.warn("Users was not found. Empty dict")
        local = {}
    # Try to fetch google spreadsheet
    try:
        google = get_users()
    except Exception as e:
        logger.exception("Google users unavailable. Local file\n" + str(e))
        return local
    else:
        if local != google:
            logger.warn("Rewriting users.json")
            with open("users.json", "w") as f:
                dump(google, f)
        return google
