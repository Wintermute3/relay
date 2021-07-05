# relay/readme-relay.md
```
05-Jul-2021
Michael Nagy
bright.tiger@gmail.com
(813) 731-1470
```
One or more _player_ (`raspberry pi` or `pi zero`) systems can accept command sequences from an _orchestrator_ (typically a `raspberry pi`) to execute gpio on/off and audio playback operations.

See also:

	README.md
	readme-pi.md
	readme-nodemcu.md
### Set up a `Raspberry Pi` as an _orchestrator_

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

### Set up the _orchestrator_

To set up the _orchestrator_, run the installation script with the _orchestrator_ option (it doesn't hurt to do so more than once):

	./pi-install.sh orchestrator
After the script finishes, you should be good.

If you run it again it should display a `success` message to confirm all went well, but otherwise do nothing.

### Test the `relay.json` file

The installer creates the `relay.json` file if it doesn't already exist, but thereafter you can edit it to add or remove _player_ systems.

Each time the `relay.py` program runs it validates the file, so it is always a good idea to run after installation, and again after each edit to the file, to assure it is still valid:
:

	./relay.py
If `relay.py` runs without error, you are good to go.

If you add new _player_ systems to the network, assure they are added to the _orchestrator_ `arp-scan` cache by:

	./relay.py -f
You can also display the current name mapping table like this:

	./relay.py -n
To see all available options, ask for help like this:

	./relay.py -h
#
