# repo: relay

this repo contains three distinct subprojects, all of which are designed to play nicely together.  the driving program, `relay.py`, sends command sequences to collections of `zero-server.py` and `wifi-relay.ino` clients to enable wifi-mediated relay-closures and audio playback.

## relay.py

wifi client control with automatic arp resolution of `mac` addresses, this program is the orchestrator of a collection of clients running on `arduino`, `pi zero` or `raspberry pi` targets

it is configured via a `relay.json` file which maps `mac` addresses to simple target names, and implements `arp` logic to locate targets specified by name using their `mac` addresses as long as they are on the same local network segment

the `relay.py` program is designed to easily invoked by keybinding macros or other programs such as `wav-player`, which is in a parallel repo

## zero-server.py / zero-player.py

these programs are designed to run on `pi zero` systems, and support both gpio relay control and audio playback via an external usb audio adapter such as the el-cheapo Sabrent stereo unit.  they are configured using the `zero.config` yaml file

the `zero-server.py` program runs as a systemd service on the `pi zero`, and accepts command lines compatible with the `wifi-relay.ino` program, but in addition supports an additional control character: an asterisk.  each time an asterisk is encountered in a command sequence, audio playback of the configured audio source is triggered.  for instance, once set up, a simple command-line to the `relay.py` program can combine relay on/off with audio playback like this:

    ./relay.py d4*5+10-20*

that command instructs the client named `d4` to begin audio playback immediately, wait 5 seconds, turn on its gpio output, wait another 10 seconds, turn off its gpio output, wait another 20 seconds, and finally kick off a second audio playback

## wifi-relay.ino

this program is an `arduino` sketch designed to run on `NodeMCU` modules

when configured on the same wifi network as the host running the `relay.py` program, it can be controlled via simple command-lines

see the `relay.json` file for how to coordinate the `NodeMCU` modules with the `relay.py` program

once set up, a simple command-line to the `relay.py` program like this can turn relays on or off:

    ./relay.py b2+ c3-

that command turns the relay named `b2` on and the relay named `c3` off using curl commands issued to the ip addresses discovered by arp-scan and matched to the mac addresses configured in the `relay.json` file.  more complex sequences are also possible, such as:

    ./relay.py b2+5-10+5- c3-

which turns the relay named `b2`, waits 5 seconds, turns it off, waits another 10 seconds, turns it back on, waits another 5 seconds, and finally turns it off again.  in parallel, the `c3` relay is simply turned off
