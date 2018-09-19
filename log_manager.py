#! python3
from time import strftime
from json import load, dump

# Log table
# | Timestamp | hashedUid | Username | Action |


def add_entry(hashedUid, username, action):
    try:
        with open("log.json") as f:
            dataLog = load(f)
    except FileNotFoundError:
        dataLog = {}
    timestamp = strftime("%d/%m/%Y %H:%M:%S")
    dataLog[timestamp] = {"hashedUid": hashedUid, "username": username,
                          "action": action}
    with open("log.json", "w") as f:
        dump(dataLog, f)
