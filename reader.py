#! python3
import logging
from hashlib import sha256
from RPi.GPIO import output as GPIO_output
from modules.MFRC522 import MFRC522
from user_manager import get_dict
from log_manager import add_entry
from signal import signal, SIGINT
from time import sleep
import telegram_bot as bot

logger = logging.getLogger("Reader")
logger.setLevel(logging.DEBUG)


def beep(seconds):  # Freezes the program!
    GPIO_output(31, True)
    sleep(seconds)
    GPIO_output(31, False)


class Instance():
    def __init__(self):
        self.userDict = get_dict()
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
        logger.info("Reader activated")
        GPIO_output(7, True)  # Close the door
        while not self.exit:
            status, _ = reader_request(readerType)
            if status != readerOk:
                continue
            logger.info("Card detected")
            status, uid = reader_get_uid()
            if status != readerOk:
                continue
            logger.info("The card contains a UID")
            hashedUid = sha256("".join(map(str, uid)).encode()).hexdigest()
            logger.info(hashedUid)
            try:
                value = self.userDict[hashedUid]
                if value["status"] == "AUTORIZADO":
                    logger.warn("Opening the door")
                    GPIO_output(31, True)
                    GPIO_output(7, False)
                    sleep(2)
                    GPIO_output(7, True)
                    GPIO_output(31, False)
                    action = "Acceso autorizado. Puerta abierta"
                    bot.user_opened_message(value["name"])
                else:
                    action = "Usuario vetado. Puerta cerrada"
                    bot.user_banned_message(value["name"])
                add_entry(hashedUid, value["name"], action)
            except KeyError:
                beep(.5)
                sleep(.5)
                beep(.5)
                bot.open_trial_message(hashedUid)
                add_entry(hashedUid, "Desconocido",
                          "Acceso no autorizado. Usuario desconocido")
                add_entry(hashedUid, "Desconocido", "Actualizando diccionario")
                self.userDict = get_dict()
                logger.warn("Updated users dict")
                beep(.5)
            sleep(2)
        reader = MFRC522()


if __name__ == "__main__":
    obj = Instance()
    obj.loop()
