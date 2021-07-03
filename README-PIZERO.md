## repo: relay / pi zero

```
03-Jul-2021
Michael Nagy
bright.tiger@gmail.com
(813) 731-1470
```

One or more `pi zero` clients can accept command sequences from an orchestrator (typically a `raspberry pi`) and execute gpio on/off and audio playback operations.  See the parallel `README-OVERVIEW.md` and `README-RASPBERRYPI.md` files for more information.

## starting with an unconfigured Raspberry Pi Zero, do the following:

 - assure that WiFi is connected to the Internet
 - open a command prompt
 - assure git is installed:
   - `sudo apt install git`
 - change into the 'pi' user's home directory:
   - `cd`
 - clone the wintermute3/relay project from github:
   - `git clone https://github.com/Wintermute3/relay.git`
 - change into the (just created) `relay` directory:
   - `cd relay`

## if the 'relay' directory already exists in the 'pi' home directory you will get an error!  recover like this:

 - assure you are in the right directory
   - `cd`
 - remove the `relay` directory
   - `rm -r relay`
 - clone the wintermute3/relay project from github:
   - `git clone https://github.com/Wintermute3/relay.git`
 - change into the (just created) `relay` directory:
   - `cd relay`

## run the installation script (it doesn't hurt to do so more than once):

 - run the install script:
   - `./zero-install.sh`

## verify success

After the script finishes, you should be good.  if you run it again it should display a 'success' message to confirm all went well.

## configuration and usage notes

By default, the `pi zero` is configured to use GPIO 4 as an active high output to control a relay.  That may be changed by editing the `zero.config` file after installation.  See notes in that file for details.

The audio playback file is also set in the `zero.config` file in a similar fashion.

To test from a command line on the `pi zero` itself, try a command such as:

  `~/relay/zero-player.py 1 5+2-@`
  
That should delay 5 seconds, turn on the relay, delay two seconds, turn the relay off, and start playback of the configured sound file.  The initial `1` parameter can be any integer, but is required.  It is used as a correlator when using the web interface. 
