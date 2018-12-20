import sys
import time
from utils import *
from Client import Client

c = Client()
c.start_probe_listener()
c.discover_offer_makers()
clear()
while True:
    print_header("AVAILABLE COMMANDS")
    commands = [
        "Refresh servers",
        "Select a file",
        "Show results",
        "List available Offerers",
        "Quit"
    ]

    for i, command in enumerate(commands):
        print("\t", change_style(str(i + 1) + ")", 'bold'), " ", command)

    option = input("\n" + change_style("Please enter your command", 'underline') + ": ")

    if option=="1":
        clear()
        print_header("Refresh servers")
        c.discover_offer_makers()
        print('-' * 89)
        pass

    elif option=="2":
        clear()
        print_header("Select a file")
        filepath = input("\n" + change_style("Enter absolute file path", 'underline') + ": ")
        number_of_ops = input("\n" + change_style("How many operations are there in file?", 'underline') + ": ")
        duration = input("\n" + change_style("How many seconds do these take?", 'underline') + ": ")
        clear()
        print("Waiting for the script offer to complete")
        c.broadcast_script_offer(filepath, int(duration), int(number_of_ops))
        print("Script offer sent")
        input("Press enter to continue")
        pass
    elif option=="3":
        clear()
        print_header("Show results")
        if c.offer is None:
            print("No offer and results are present at this time\n")
            print("Press Enter to continue\n")
            input()
            clear()
            continue
        success, result = c.offer.get_results()
        print(c.offer.get_offsets())

        if success:
            print(result)
        else:
            print("Could not complete operation successfully")
        print("\nPress Enter to continue")
        input()
        clear()

    elif option == "4":
        clear()
        print_header("List available servers")
        for server in c.available_servers.values():
            print(server)
        print("\nPress Enter to continue")
        input()
        clear()

    elif option=="5":
        clear()
        print_notification("Good bye \n\n")
        os.system("pkill -9 \"python3 main.py\"")
        sys.exit(0)
    else:
        clear()
        print_error("Invalid option")
