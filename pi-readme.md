# relay/pi-readme.md

```
04-Jul-2021
Michael Nagy
bright.tiger@gmail.com
(813) 731-1470
```

One or more _player_ (`raspberry pi` or `pi zero`) systems can accept command sequences from an _orchestrator_ (typically a `raspberry pi`) to execute gpio on/off and audio playback operations.

See also:

	README.md
	nodemcu-readme.md
_Note_: Henceforth `pi` will refer to either a `Raspberry Pi` or a `Pi Zero`.

### Set up a `Raspberry Pi` or `Pi Zero`

Log on as the `pi` user and assure that the `pi` is connected to your WiFi (which is assumed to give access to the Internet).

Get a command prompt and assure git is installed:

	sudo apt install git
Change into the `pi` user's home directory and check to see if the `relay` directory already exists:

	cd
	ls -al
Get an up-to-date copy of the `relay` repo as follows:

If the `relay` directory does not exist, do this:

	git clone https://github.com/Wintermute3/relay.git
	cd relay
If the `relay` directory does exist, do this instead:

	cd relay
	git pull
Either way, you should now be in the `relay` directory with an up-to-date copy of the repo.	

### Set up an _orchestrator_ (Raspberry Pi only)

To set up an _orchestrator_, run the installation script with the _orchestrator_ option (it doesn't hurt to do so more than once):

	./pi-install.sh orchestrator
After the script finishes, you should be good.

If you run it again it should display a `success` message to confirm all went well, but otherwise do nothing.
### Set up a _player_ (Raspberry Pi or Pi Zero)

To set up a _player_, run the installation script with the _player_ option (it doesn't hurt to do so more than once):

	./pi-install.sh player
After the script finishes, you should be good.

If you run it again it should display a `success` message to confirm all went well, but otherwise do nothing.
### Usage

By default, the `pi` is configured to use GPIO 4 as an active high output to control a relay.  That may be changed by editing the `pi-player.config` file after installation.  See notes in that file for details, and see this for pinouts:

	https://www.raspberrypi.org/documentation/usage/gpio/images/GPIO-Pinout-Diagram-2.png
The audio playback file is also set in the `pi-player.config` file in a similar fashion.  Audio playback is via an external usb audio adapter such as the el-cheapo Sabrent stereo unit.

To test from a command line on the `player` itself, try a command such as:

	~/relay/pi-player.py 1 5+2-@
That should delay 5 seconds, turn on the relay, delay two seconds, turn the relay off, and start playback of the configured sound file.  The initial `1` parameter can be any integer, but is required.  It is used as a correlator when using the web interface.

#
