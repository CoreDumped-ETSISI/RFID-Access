#! python3
from google_api import insert_user
from google_api import get_users
from json import load, dump


def add_entry(hashedUid, status, name, email, phone, telegramName):
    with open("users.json") as f:
        userData = load(f)
    insert_user(hashedUid, status, name, email, phone, telegramName)
    userData[hashedUid] = {"status": status, "name": name, "email": email,
                           "phone": phone, "telegramName": telegramName}
    with open("users.json", "w") as f:
        dump(userData, f)


def get_dict():
    try:
        userData = get_users()
    except Exception:
        with open("users.json") as f:
            userData = load(f)
    return userData
