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
        pass
    elif option=="2":
        pass
    elif option=="3":
        pass
    elif option=="4":
        clear()
        print_notification("Good bye \n\n")
        os.system("pkill -9 \"python3 main.py\"")
        sys.exit(0)
    else:
        clear()
        print_error("Invalid option")
