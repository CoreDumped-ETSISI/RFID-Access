#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telepot

vip_chat_id = 1001104852034

token = {}
tokenfile = open("credenciales.txt", "r")
token["Telegram"] = tokenfile.readline()
tokenfile.close()
bot = telepot.Bot(token["Telegram"])


def user_opened_message(name):
    bot.sendMessage(vip_chat_id, name + " ha habierto el local.")


def user_banned_message(name):
    bot.sendMessage(vip_chat_id, name + " ha intentado abrir el local.")


def open_trial_message(hashed_uid):
    bot.sendMessage(vip_chat_id,
                    "Alguien con hash terminado en "
                    + str(hashed_uid)[-8:]
                    + "ha intentado abrir el local.")
