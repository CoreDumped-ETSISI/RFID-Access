import RPi.GPIO as GPIO
import MFRC522
import signal

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# in this action the RFID reader waits for a card, which if don't exist in the database, will be added on it
def new_user():
    global continue_reading
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
                pass    # TODO: here we should check if the captured uid already exist in the database and add it

# this action prints a list of all the users
def show_users():
    pass    # TODO: print a list of all the users

# this action erases the target user fro the database
def delete_user():
    pass    # TODO: erase the target user fro the database

# this action shows the personal data of target user
def user_data():
    pass    # TODO: show the personal data of target user


def default():
    print("\nPlease choose a correct option\n")
    pass


def main():
    sentinel = True
    d_actions = {
        1: new_user,
        2: show_users,
        3: delete_user,
        4: user_data,
    }
    actions_list = ["New user", "Show users", "Delete user", "User data"]
    while sentinel:
        for x in list(d_actions):
            print(x, actions_list[x-1])
        print(0, "Exit")
        sec = int(input("Select: "))
        if sec != 0:
            d_actions.get(sec,default)()
        else:
            sentinel = False


if __name__ == "__main__":
    main()