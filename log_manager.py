#! python3
from time import strftime


def add_entry(hashedUid, username, action):
    timestamp = strftime("%d/%m/%Y %H:%M:%S")
    with open("log.txt", "a") as f:
        f.write(";".join((timestamp, hashedUid, username, action)))
