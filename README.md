# relay
wifi relay control with automatic arp resolution of mac addresses

the Arduino wifi-relay.ino sketch will run on a NodeMCU module, and when configured for the same wifi network as the host for the python3 relay.py program, can be controlled via simple command-lines

see the relay.json file for how to coordinate the NodeMCU modules with the python program.

once set up, a simple command-line like this can turn relays on or off:

    ./relay.py b2+ c3-

that command turns the relay named 'b2' on and the relay named 'c3' off using curl commands issued to the ip addresses discovered by arp-scan and matched to the mac addresses configured in the 'relay.json' file.
