import sys
import time
from utils import *

clear()
while True:
    print_header("AVAILABLE COMMANDS")
    commands = [
        "Refresh servers",
        "Select a file",
        "Show results",
        "Quit"
    ]

    for i, command in enumerate(commands):
        print("\t", change_style(str(i + 1) + ")", 'bold'), " ", command)

    option = input("\n" + change_style("Please enter your command", 'underline') + ": ")

    if option=="1":
        clear()
        print_header("Refresh servers")
        print('-' * 89)

        pass
    elif option=="2":
        clear()
        print_header("Select a file")
        filepath = input("\n" + change_style("Enter absolute file path", 'underline') + ": ")
        number_of_ops = input("\n" + change_style("How many operations are there in file?", 'underline') + ": ")
        duration = input("\n" + change_style("How many seconds do these take?", 'underline') + ": ")
        print("OK hacim")
        pass
    elif option=="3":
        clear()
        print_header("Show results")
        pass
    elif option=="4":
        clear()
        print_notification("Good bye \n\n")
        os.system("pkill -9 \"python3 main.py\"")
        sys.exit(0)
    else:
        clear()
        print_error("Invalid option")
