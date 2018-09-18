#! python3
import logging
from telegram import Bot

logger = logging.getLogger("TelegramBot")
logger.setLevel(logging.DEBUG)

VIP_CHAT_ID = -1001104852034
with open("credenciales.txt") as f:
    TOKEN = f.readline()
BOT = Bot(TOKEN)


def user_opened_message(name):
    try:
        BOT.send_message(text="%s ha abierto el local." % name,
                         chat_id=VIP_CHAT_ID)
    except Exception as e:
        logger.exception("Error al mandar el mensaje\n" + str(e))


def user_banned_message(name):
    try:
        BOT.send_message(text="%s ha intentado abrir el local." % name,
                         chat_id=VIP_CHAT_ID)
    except Exception as e:
        logger.exception("Error al mandar el mensaje\n" + str(e))


def open_trial_message(hashedUid):
    try:
        BOT.send_message(text="Alguien con hash terminado en %s ha intentado"
                         " abrir el local." % hashedUid[-8:],
                         chat_id=VIP_CHAT_ID)
    except Exception as e:
        logger.exception("Error al mandar el mensaje\n" + str(e))
