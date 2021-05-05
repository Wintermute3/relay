## repo: relay / pi zero

```
04-May-2021
Michael Nagy
bright.tiger@gmail.com
(813) 731-1470
```

A `pi zero` is a client which can accept command sequences from an orchestrator (typically a `raspberry pi`) and execute gpio on/off and audio playback operations.  See the parallel `README-OVERVIEW.md` and `README-RASPBERRYPI.md` files for more information.

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
   - `rm -f relay`
 - clone the wintermute3/relay project from github:
   - `git clone https://github.com/Wintermute3/relay.git`
 - change into the (just created) `relay` directory:
   - `cd relay`
 - update the contents to the latest version:
   - `git pull`

## run the installation script (it doesn't hurt to do so more than once):

 - run the install script:
   - `./zero-install.sh`

## verify success

After the script finishes, you should be good.  if you run it again
it should display a 'success' message to confirm all went well.
