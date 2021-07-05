# relay/readme-nodemcu.md

```
04-Jul-2021
Michael Nagy
bright.tiger@gmail.com
(813) 731-1470
```

One or more `nodemcu-player` systems can accept command sequences from an orchestrator (typically a `raspberry pi`) and execute gpio on/off.

See also:

	README.md
	readme-pi.md
	readme-relay.md
### Set up a `NodeMCU` player

These instructions are generic, as it is possible to set up the `NodeMCU` from any system that can run the `Arduino IDE` and clone a `git` repo.

### Configure the sketch

On your workstation:

- clone the repo: `https://github.com/Wintermute3/relay.git`
- open the file `nodemcu-player.ino` in the repo directory using the `Arduino IDE`
- edit it to add your WiFi credentials to the `WiFiNetworks` table

### Configure the hardware

- connect your relay board to the `NodeMCU` using D0
- connect your `NodeMCU` module to your workstation
- open a terminal window to your `NodeMCU` at 115200 baud
- upload the sketch to your `NodeMCU` module
- watch the terminal to see your `NodeMCU` connect to your WiFi network
- note its `IP` and `MAC` addresses as reported on the terminal

You can now use those addresses to add an entry in the `relay.json` file on your orchestrator, and then test your new player using that name.
#
