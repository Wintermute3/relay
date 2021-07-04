# relay/README.md

```
04-Jul-2021
Michael Nagy
bright.tiger@gmail.com
(813) 731-1470
```

This repo contains several components which are designed to play nicely together using the `player` protocol.

### relay.py

The program `relay.py` runs on the _orchestrator_ system (expected to be a `raspberry pi`) and sends _player_ command sequences over WiFi to instances of `raspberry pi`, `pi zero` and `nodemcu` _clients_ to control relay-closures and audio playback.

It finds WiFi client addresses using automatic arp resolution (discovery) of `mac` addresses.

It is configured via the `relay.json` file which maps `mac` addresses to simple target names, and implements `arp` logic to locate targets specified by name using their `mac` addresses as long as they are on the same local network segment.

The `relay.py` program is designed to be easily invoked by `xkeybind` macros (or other programs such as `wav-player`, which is in a different repo).

### pi-server.py / pi-player.py

These programs are designed to run on `raspberry pi` or `pi zero` systems, and support both gpio relay control and audio playback via an external usb audio adapter such as the el-cheapo Sabrent stereo unit.

See also:

	pi-readme.md
They are configured using the `pi-player.config` yaml file.

The `pi-server.py` program runs as a systemd service, and accepts command lines compatible with the `nodemcu-player.ino` program, but in addition supports two additional control characters: an ampersand `@` and an percent sign `%`.

Each time an ampersand is encountered in a command sequence, audio playback of the configured audio source is triggered, and each time an percent sign is encountered, any active audio playback is immediately aborted.

For instance, once set up, a simple command-line to the `relay.py` program can combine relay on/off with audio playback like this:

	./relay.py d4@5+10-20@
That command instructs the `player` client named `d4` to begin audio playback immediately, wait 5 seconds, turn on its gpio output, wait another 10 seconds, turn off its gpio output, wait another 20 seconds, and finally kick off a second audio playback.

### nodemcu-player.ino

This program is an `arduino` sketch designed to run on `NodeMCU` modules.

See also:

	nodemcu-readme.md
Except for lack of audio playback support, it is compatible with the other `player` clients.

When configured on the same WiFi network as the host running the `relay.py` program, it can be controlled via simple command-lines.

See the `relay.json` file for how to coordinate the `NodeMCU` modules with the `relay.py` program.

Once set up, a simple command-line to the `relay.py` program like this can turn relays on or off:

	./relay.py b2+ c3-
That command turns the relay named `b2` on and the relay named `c3` off using curl commands issued to the ip addresses discovered by _arp-scan_ and matched to the mac addresses configured in the `relay.json` file.

More complex sequences are also possible, such as:

	./relay.py b2+5-10+5- c3-
Which turns the relay named `b2`, waits 5 seconds, turns it off, waits another 10 seconds, turns it back on, waits another 5 seconds, and finally turns it off again.  in parallel, the `c3` relay is simply turned off

#
