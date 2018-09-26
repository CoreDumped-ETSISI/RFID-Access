#!usr/bin/env python3
import logging
from hashlib import sha256
from modules.MFRC522 import MFRC522
from RPi.GPIO import output as GPIO_output
from signal import signal, SIGINT
from time import sleep
from getter import Getter
import setter

logger = logging.getLogger("Reader")
logger.setLevel(logging.DEBUG)


def beep(seconds):  # Freezes the program!
    GPIO_output(31, True)
    sleep(seconds)
    GPIO_output(31, False)


class Reader(Getter):
    def __init__(self):
        Getter.__init__(self)
        self.exit = False

    def end_read(self, *arg):
        """Capture SIGINT for cleanup when the script is aborted"""
        logger.warn("Ctrl-C captured. Ending read.")
        self.exit = True

    def loop(self):
        signal(SIGINT, self.end_read)
        reader = MFRC522()
        reader_request = reader.MFRC522_Request
        reader_get_uid = reader.MFRC522_Anticoll
        readerType = reader.PICC_REQIDL
        readerOk = reader.MI_OK
        logger.warn("Reader activated")
        GPIO_output(7, True)  # Close the door
        while not self.exit:
            status, _ = reader_request(readerType)
            if status != readerOk:
                continue
            logger.warn("Card detected")
            status, uid = reader_get_uid()
            if status != readerOk:
                continue
            logger.warn("The card contains a UID")
            hashedUid = sha256("".join(map(str, uid)).encode()).hexdigest()
            logger.warn(hashedUid)
            try:
                value = self.users[hashedUid]
                if value["status"] == "AUTORIZADO":
                    logger.warn("Opening the door")
                    GPIO_output(31, True)
                    GPIO_output(7, False)
                    sleep(2)
                    GPIO_output(7, True)
                    GPIO_output(31, False)
                    action = "Acceso autorizado. Puerta abierta"
                    setter.user_opened_message(value["name"])
                else:
                    action = "Usuario vetado. Puerta cerrada"
                    setter.user_banned_message(value["name"])
                setter.add_entry(hashedUid, value["name"], action)
            except KeyError:
                beep(.5)
                sleep(.5)
                beep(.5)
                setter.open_trial_message(hashedUid)
                setter.open_trial_message(hashedUid)
                setter.add_entry(hashedUid, "Desconocido",
                                 "Acceso no autorizado. Usuario desconocido")
                self.get_users()
                beep(.5)
            sleep(2)
            reader = MFRC522()
            beep(.2)

if __name__ == "__main__":
    obj = Reader()
    obj.loop()
