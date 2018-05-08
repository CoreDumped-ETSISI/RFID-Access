#!/usr/bin/env python
import RPi.GPIO as GPIO
import MFRC522
import signal
import time
from google_api_connector import get_users_json
import hashlib

sentinel = True
continue_reading = True

# We will use this global variables in TIMER()
main_timer = 0
times_between_denieds_list = [0]
times_denied = 0
start_timer = 0

#Use those to choose how many calls in how much time(in secs) you want to call BLOCK()
max_denied = 5
max_time = 30

# Use this one to choose how much time will be the reader stopped (in secs)
blocked_time = 30

# This stops the script and clean the raspberry pins
def end_read(signal,frame):
    global sentinel
    global continue_reading
    print "Ctrl+C captured, ending read."
    sentinel = False
    continue_reading = False
    GPIO.cleanup()

# When this has been called max_denies times in max_time secs, calls BLOCK()
def brute_force_avoid():
    global main_timer
    global times_between_denieds_list
    global times_denied
    global start_timer
    global max_denied
    global max_time
    if times_denied > 0:
        end_timer = time.time()
        times_between_denieds_list = times_between_denieds_list + [end_timer - start_timer]
        main_timer = main_timer + (end_timer - start_timer)
    start_timer = time.time()
    times_denied += 1
    # A double blink-LED in denied case
    GPIO.output(31, True)
    time.sleep(0.5)
    GPIO.output(31, False)
    time.sleep(0.2)
    GPIO.output(31, True)
    time.sleep(0.5)
    GPIO.output(31, False)
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

# This calls the remote database and return a dictionary with the users data
def get_codebook():
    book = get_users_json()
    return book

def hasher(str):
    return hashlib.md5(str).hexdigest()

def open_door():
    print("OPEN ...")
    GPIO.output(31, True)
    GPIO.output(7, False)
    time.sleep(4)
    GPIO.output(7, True)
    GPIO.output(31, False)


signal.signal(signal.SIGINT, end_read) # This calls end_read when the program capture Ctrl+C
codebook = get_codebook()
print("Reader activated")
while sentinel:
    continue_reading = True
    MIFAREReader = MFRC522.MFRC522() # We create an object which drives the hardware
    GPIO.output(7, True)
    while continue_reading:
        (detected,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL) # This scan for new cards
        (status,uid) = MIFAREReader.MFRC522_Anticoll() # This takes the uid card as a list called uid
        if detected == MIFAREReader.MI_OK:
            print("Card detected")
        if status == MIFAREReader.MI_OK:
            hash_uid = hasher(''.join(str(e) for e in uid))
            print(uid)
            if hash_uid in codebook and codebook[hash_uid]["status"] == "AUTORIZADO":  # TODO: Call a log
                open_door()
                continue_reading = False
            else:
                brute_force_avoid()