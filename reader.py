#!/usr/bin/env python
import hashlib
import signal
import time

import RPi.GPIO as GPIO

import MFRC522
import telegram_bot as bot
from log_manager import new_log_entry
from user_manager import get_user_dictionary

reset_reader_sentinel = True
continue_reading = True

# We will use this global variables in TIMER()
main_timer = 0
times_between_denieds_list = [0]
times_denied = 0
start_timer = 0

# Use those to choose how many calls in how much time(in secs) you want to call BLOCK()
max_denied = 5
max_time = 30

# Use this one to choose how much time will be the reader stopped (in secs)
blocked_time = 30


# This stops the script and clean the raspberry pins
def end_read(signal, frame):
    global reset_reader_sentinel
    global continue_reading
    print "Ctrl+C captured, ending read."
    reset_reader_sentinel = False
    continue_reading = False
    GPIO.cleanup()


def led_denial_blink():
    for _ in (0, 3):
        GPIO.output(31, True)
        time.sleep(0.1)
        GPIO.output(31, False)
        time.sleep(0.1)


# When this has been called max_denies times in max_time secs, calls BLOCK()
def brute_force_avoid():
    global main_timer
    global times_between_denieds_list
    global times_denied
    global start_timer
    global max_denied
    global max_time
    global blocked_time
    if times_denied > 0:
        end_timer = time.time()
        times_between_denieds_list = times_between_denieds_list + [end_timer - start_timer]
        main_timer = main_timer + (end_timer - start_timer)
    start_timer = time.time()
    times_denied += 1
    led_denial_blink()
    if times_denied == max_denied:
        if main_timer <= max_time:
            #
            GPIO.output(31, True)
            time.sleep(blocked_time)
            GPIO.output(31, False)
            main_timer = 0
            times_denied = 0
            times_between_denieds_list = [0]
        else:
            main_timer -= times_between_denieds_list[0]
            times_between_denieds_list = times_between_denieds_list[1:]
            times_denied -= 1


def hasher(string):
    return hashlib.sha256(string).hexdigest()


def open_door():
    print("OPEN ...")
    GPIO.output(31, True)
    GPIO.output(7, False)
    time.sleep(2)
    GPIO.output(7, True)
    GPIO.output(31, False)


def is_user_authorized(hashed_uid):
    if hashed_uid in users_data:
        if users_data[hashed_uid]["status"] == "AUTORIZADO":
            return True
    else:
        return False


def is_user_denied(hashed_uid):
    if hashed_uid in users_data:
        if users_data[hashed_uid]["status"] == "VETADO":
            return True
    else:
        return False


signal.signal(signal.SIGINT, end_read)  # This calls end_read when the program capture Ctrl+C
users_data = get_user_dictionary()
print("Reader activated")
while reset_reader_sentinel:
    continue_reading = True
    MIFAREReader = MFRC522.MFRC522()  # We create an object which drives the hardware
    GPIO.output(7, True)
    while continue_reading:
        (card_detected, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)  # This scan for new cards
        (status, uid) = MIFAREReader.MFRC522_Anticoll()  # This takes the uid card as a list called uid
        if card_detected == MIFAREReader.MI_OK:
            print("Card detected")
        if status == MIFAREReader.MI_OK:
            hashed_uid = hasher(''.join(str(e) for e in uid))
            print(hashed_uid)
            continue_reading = False
            if is_user_authorized(hashed_uid):  # Usuario autorizado
                open_door()
                new_log_entry(hashed_uid, users_data[hashed_uid]["name"], "Acceso autorizado, puerta abierta")
                bot.user_opened_message(users_data[hashed_uid]["name"])
            elif is_user_denied(hashed_uid):  # Usuario vetado
                new_log_entry(hashed_uid, users_data[hashed_uid]["name"], "Usuario vetado, puerta cerrada")
                bot.user_banned_message(users_data[hashed_uid]["name"])
            else:
                new_log_entry(hashed_uid, "Desconocido", "Acceso no autorizado, usuario desconocido")
                bot.open_trial_message(hashed_uid)
                brute_force_avoid()
