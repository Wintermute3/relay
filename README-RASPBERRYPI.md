## repo: relay / raspberry pi

```
02-May-2021
Michael Nagy
bright.tiger@gmail.com
(813) 731-1470
```

A `raspberry pi` is the preferred orchestrator for a constellation of `relay` and `pi zero` clients.  See the parallel `README-OVERVIEW.md` and `README-PIZERO.md` files for more information.

To set up a `raspberry pi` as an orchestrator, proceed as follows:

## starting with an unconfigured Raspberry Pi, do the following:

 - assure that WiFi is connected to the Internet
 - open a command prompt
 - assure git is installed:
   - `sudo apt install git`
 - change into the 'pi' user's home directory:
   - `cd`

## if the 'relay' directory already exists in the 'pi' home directory, then update it like this:

 - change into the 'relay' directory:
   - `cd relay`
 - update the contents to the latest version:
   - `git pull`

## ...otherwise, create it like this:

 - clone the wintermute3/relay project from github:
   - `git clone https://github.com/Wintermute3/relay.git`
 - change into the relay directory:
   - `cd relay`

## run the installation script (it doesn't hurt to do so more than once):

 - run the install script:
   - `./pi-install.sh`

## verify success

After the script finishes, you should be good to go inserting 'relay'
commands in the key bindings configuration file.  if you run it again
it should display a 'success' message to confirm all went well.
