import RPi.GPIO as GPIO
import MFRC522
import signal
import hashlib
import user_manager as users
from user_manager import get_user_dictionary


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()


# This returns hashed str
def hasher(string):
    return hashlib.sha256(string).hexdigest()


continue_reading = True
users_dictionary = get_user_dictionary()


# in this action the RFID reader waits for a card, which if don't exist in the database, will be added on it
def new_user():
    global continue_reading
    global users_dictionary
    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)
    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()
    # Welcome message
    print("Introduce tu tag")
    print("Press Ctrl-C to stop.")
    # This loop keeps checking for chips. If one is near it will get the UID
    continue_reading = True
    while continue_reading:
        # Scan for cards
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        # If a card is found
        if status == MIFAREReader.MI_OK:
            print("Card detected")
            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:
                hash_uid = hasher(''.join(str(e) for e in uid))
                if not (hash_uid in users_dictionary):
                    name = raw_input("Name: ")
                    email = raw_input("Email: ")
                    phone = raw_input("Phone: ")
                    telegram_name = raw_input("Telegram nick: ")
                    users.new_user_entry(hash_uid, "AUTORIZADO", name, email, phone, telegram_name)
                    users_dictionary = get_user_dictionary()
                else:
                    print("Tag already exists")
                continue_reading = False
                GPIO.cleanup()


# this action prints a list of all the users
def show_users():
    global users_dictionary
    for key, dt in users_dictionary.items():
        print(key + " -> " + dt["name"])
        print("     - Email: " + dt["email"])
        print("     - Phone: " + dt["phone"])
        print("     - Telegram user: " + dt["telegram_user"])
        print("     - Status: " + dt["status"] + "\n")


def default():
    print("\nPlease choose a correct option\n")
    pass


def main():
    sentinel = True
    d_actions = {
        1: new_user,
        2: show_users
    }
    actions_list = ["New user", "Show users"]
    while sentinel:
        for x in list(d_actions):
            print(x, actions_list[x - 1])
        print(0, "Exit")
        sec = int(input("Select: "))
        if sec != 0:
            d_actions.get(sec, default)()
        else:
            sentinel = False


if __name__ == "__main__":
    main()
