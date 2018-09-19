#! python3
import logging
from hashlib import sha256
from RPi.GPIO import cleanup as GPIO_cleanup
from modules.MFRC522 import MFRC522
from user_manager import add_entry, get_dict
from signal import signal, SIGINT

logger = logging.getLogger("AdminConsole")
logger.setLevel(logging.DEBUG)

USERS_PRESET = """
%s -> %s
     - Email: %s
     - Phone: %s
     - Telegram user: %s
     - Status: %s
"""


class Instance():
    def __init__(self):
        self.userDict = get_dict()
        self.exit = False

    def end_read(self, *arg):
        """Capture SIGINT for cleanup when the script is aborted"""
        logger.warn("Ctrl-C captured. Ending read.")
        self.exit = True

    def new_user(self):
        signal(SIGINT, self.end_read)
        reader = MFRC522()
        reader_request = reader.MFRC522_Request
        reader_get_uid = reader.MFRC522_Anticoll
        readerType = reader.PICC_REQIDL
        readerOk = reader.MI_OK
        logger.warn("Introduce your tag\nPress Ctrl-C to stop")
        while not self.exit:
            status, _ = reader_request(readerType)
            if status != readerOk:
                continue
            logger.warn("Card detected")
            status, uid = reader_get_uid()
            if status != readerOk:
                continue
            logger.warn("The card contains a UID")
            hashedUid = sha256("".join(map(str, uid))).hexdigest()
            if hashedUid not in self.userDict:
                name = input("Name: ")
                email = input("Email: ")
                phone = input("Phone: ")
                telegramName = input("Telegram nick: ")
                add_entry(hashedUid, "AUTORIZADO", name, email,
                          phone, telegramName)
                self.userDict = get_dict()
            else:
                logger.warn("Tag already exists")
            self.exit = True
            GPIO_cleanup()

    def show_users(self):
        for key, dt in self.userDict.items():
            logger.warn(USERS_PRESET % (key, dt["name"], dt["email"],
                                        dt["phone"], dt["telegramUser"],
                                        dt["status"]))


def main():
    obj = Instance()
    actions = [("Exit", 0), ("New user", obj.new_user),
               ("Show users", obj.show_users)]
    while True:
        for a, i in enumerate(actions):
            logger.warn("%d: %s" % (a, i))
        selection = int(input("Select: "))
        if selection == 0:
            break
        elif 0 < selection < 3:
            actions[selection][1]()
        else:
            logger.warn("Wrong option! (%d)" % selection)


if __name__ == "__main__":
    main()
