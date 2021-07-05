# relay/README.md

```
05-Jul-2021
Michael Nagy
bright.tiger@gmail.com
(813) 731-1470
```

This repo contains several components which are designed to play nicely together using the `player` protocol.

Files in the repo include:

	nodemcu-player.ino . . . Arduino sketch for NodeMCU modules
	pi-install.sh  . . . . . bash install script for all pi systems
	pi-player.default  . . . template for pi player config file
	pi-player.py . . . . . . pi player python3 program
	pi-player.service  . . . pi player systemd unit file
	pi-server.py . . . . . . pi server python3 program
	pulseaudio.service . . . pulse audio systemd unit file
	README.md  . . . . . . . this file
	readme-nodemcu.md  . . . instructions for NodeMCU setup
	readme-pi.md . . . . . . instructions for player setup
	readme-relay.md  . . . . instructions for orchestrator setup
	relay  . . . . . . . . . proxy bash script for relay.py program
	relay.default  . . . . . template for orchestrator config file
	relay.py . . . . . . . . orchestrator python3 program
	
	.gitignore . . . . . . . lists files which git should ignore
The following files are not part of the repo, but will exist on _orchestrator_ or _player_ systems:
	
	pi-player.config . . . . player config file, make any edits here
	pi-player.status . . . . player status file, most recent run
	relay.json . . . . . . . orchestrator config file, make edits here
	relay.peer . . . . . . . orchestrator arp-scan cache file
These files are listed in the `.gitignore` file.
### relay.py

The program `relay.py` runs on the _orchestrator_ system (expected to be a `raspberry pi`) and sends _player_ command sequences over WiFi to instances of `raspberry pi`, `pi zero` and `nodemcu` _players_ to control relay-closures and audio playback.

See also:

	readme-relay.md . . . . installation instructions
It finds WiFi client addresses using automatic arp resolution (discovery) of `mac` addresses.

It is configured via the `relay.json` file which maps player names to `mac` addresses, and implements `arp-scan` logic to locate targets specified by name using their `mac` addresses as long as they are on the same local network segment.

The `relay.py` program is designed to be easily invoked by `xkeybind` macros (or other programs such as `wav-player`, which is in a different repo).  A convenient proxy script named `relay` is provided to make this as concise as possible.

### pi-server.py / pi-player.py

These programs are designed to run on `raspberry pi` or `pi zero` systems, and support both gpio relay control and audio playback via an external usb audio adapter such as the el-cheapo Sabrent stereo unit.

See also:

	readme-pi.md . . . . installation instructions
They are configured using the `pi-player.config` yaml file.

The `pi-server.py` program runs as a systemd service, and accepts command lines compatible with the `nodemcu-player.ino` program.

See the `relay.json` file for how to coordinate the `pi` modules with the `relay.py` program.

### nodemcu-player.ino

This program is an `arduino` sketch designed to run on `NodeMCU` modules.

See also:

	readme-nodemcu.md . . . . installation instructions
Except for lack of audio playback support, it is compatible with the other `player` systems.

When configured on the same WiFi network as the host running the `relay.py` program, it can be controlled via simple command-lines.

See the `relay.json` file for how to coordinate the `NodeMCU` modules with the `relay.py` program.
### player protocol
All _player_ systems support a compatible command-string format via the `relay.py` program.  Each command-string consists of a `player name` (expected to map to a `mac` address via the `relay.json` file) followed by a string of characters which control relay on/off, audio playback, and delays.
##### relay control

Once set up, a simple command-line to the `relay.py` program like this can turn relays on or off:

	./relay.py b2+ c3-
That command turns the relay on the player named `b2` on and the relay on the player named `c3` off using curl commands issued to the ip addresses discovered by _arp-scan_ and matched to the mac addresses configured in the `relay.json` file.

More complex sequences are also possible, such as:

	./relay.py b2+5-10+5- c3-
Which turns the `b2` player relay on, waits 5 seconds, turns it off, waits another 10 seconds, turns it back on, waits another 5 seconds, and finally turns it off again.  In parallel, the `c3` player relay is simply turned off.

##### audio playback (`pi` players only) 

Audio playback is started with the `@` (ampersand) character, and can be terminated explicitly with the `%` (percent) character.  If not terminated explicitly, audio output ends naturally with the end of the audio stream.

	./relay.py delta-5+2-@
That targets the player named `delta`, delays 5 seconds, turns on the relay, delays two seconds, turns the relay off, and then starts playback of the configured sound file.  Note: The initial `-` is ineffective, but serves to delimit the player name.

Another example:

	./relay.py delta@5+10-20@
That command instructs the player named `delta` to begin audio playback immediately, wait 5 seconds, turn on its relay, wait another 10 seconds, turn off its relay, wait another 20 seconds, and finally kick off a second audio playback.
#### end
#
