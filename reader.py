#!/usr/bin/env python
import RPi.GPIO as GPIO
import MFRC522
import signal
import time

sentinel = True
continue_reading = True

# We will use this global variables in TIMER()
timer = 0
time_list = [0]
times_denied = 0
start_timer = 0

#Use those to select how many calls in how much time(in secs) you want to call BLOCK()
max_denied = 5
max_time = 30


def end_read(signal,frame):
    global sentinel
    global continue_reading
    print "Ctrl+C captured, ending read."
    sentinel = False
    continue_reading = False
    GPIO.cleanup()

# This update the log and freeze the loop by 30 sec
def BLOCK():
    time.sleep(30)

# When this has been called 5 times in 30 sec, calls BLOCK()
def TIMER():
    global timer
    global time_list
    global times_denied
    global start_timer
    global max_denied
    global max_time
    if times_denied > 0:
        end_timer = time.time()
        time_list = time_list + [end_timer - start_timer]
        timer = timer + (end_timer - start_timer)
    start_timer = time.time()
    times_denied += 1
    if times_denied == max_denied:
        if timer <= max_time:
            BLOCK()
            timer = 0
            times_denied = 0
            time_list = [0]
        else:
            timer -= time_list[0]
            time_list = time_list[1:]
            times_denied -= 1


signal.signal(signal.SIGINT, end_read)
while sentinel:
    continue_reading = True
    abrir_puerta = False
    MIFAREReader = MFRC522.MFRC522()
    GPIO.output(7, True)
    while continue_reading:
        if abrir_puerta:
            print("Puerta Abierta")
            GPIO.output(7, False)
            time.sleep(2)
            GPIO.output(7, True)
            abrir_puerta = False
            continue_reading = False
        (detected,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        (status,uid) = MIFAREReader.MFRC522_Anticoll()
        if detected == MIFAREReader.MI_OK:
            print("Card detected")
        if status == MIFAREReader.MI_OK:
            if True:    # TODO: here we should call a database authenticator and not True
                abrir_puerta = True
            else:
                TIMER()