# Distributed Map Reduce

### Contributors  
- [M. Hakan Kurtoğlu](https://github.com/memhak)  
- [A. Emirhan Karagül](https://github.com/emir350z)
- Special Thanks to [Enes Çakır](https://github.com/EnesCakir) as we used the command line interface skeleton from the [project](https://github.com/CMPE487/torrent-chat-emir350z) we have implemented together

### Execution
Before you run make sure that you are using python version 3.7,  
To install the requirements type   
`pip3 install -r requirements.txt` into your shell.  
If you want to offer your pc as a resource to the network run:  
`python3 Server.py` and proceed with the instructions that are prompted. 
Else if you want to use the networks resources run:  
`python3 main.py` and proceed with the prompted instructions in the program.  
If you are using this program on mac you should install coreutils to use gtimeout by the following command in your shell:  
`brew install coreutils`

### Disclaimer  
- Virtual Enironment dependencies are under requirements.txt .
- Need to have Python 3.7 to use the latest modules of asyncio and to run this project.
- Need to have a Linux environment for using the timeout command in Server.py 
- Good news for Windows users! It also works on Ubuntu Subsystem on Windows. :) 
- Mac environment is also supported by the installation of coreutils. (It's not tested)
- You can find an example script (example_script.py) for using distributed map reduce with its required syntax.

### Project Definition
![Flow](https://github.com/CMPE487/final-project-distributedmapreduce/blob/master/report/flow.png?raw=true)
- Constants are defined in thefile config.py
- Servers have 2 connection handlers. 1 for discovery requests on UDP and 1 on script offer and script content transmission on TCP.
- Servers wait for script offers and respond positively if they are not busy, after they respond they lock theirselves for a time interval defined in the config, if they do not receive the script content they release theirselves and become available again.
- If servers receive script content they execute it for the promised time quant with a little more tolerance. They will cancel execution if the operations take longer and it will send the results of the completed operations
- Clients have 3 connection handlers. 1 for discovery requests on UDP, 1 for offering scripts and 1 for sending script content and receiving results.
- Clients have a simple UI to interact with.
- Asyncio transports are used to implement connection handlers on TCP and UDP
- Clients check the available servers after sending script offers, if the available resources are greater than the required resource for the task they send the script content, otherwise they will prompt error and stop the sequence
- After they send the scripts, they wait for the calculated time + a little tolerance to gather the results, if they do not receive they close the connections and prompt error to the user

