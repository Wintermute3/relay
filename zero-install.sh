#!/bin/bash

PROGRAM='zero-install.sh'
VERSION='2.104.271'
CONTACT='bright.tiger@mail.com' # michael nagy

#============================================================================
# set things up so that zero-server.py autostarts on boot and do a couple
# of other more minor house-keeping things.
#============================================================================

echo

# assure we are in the 'pi' user's home directory
cd /home/pi/relay

DELTA=0

# assure nagy's favorite aliases are installed
if grep '^alias ll=' ~/.bashrc > /dev/null; then
  echo the ll alias is installed
else
  echo "alias ll='ls -lh'" >> ~/.bashrc
  echo installed the ll alias
  DELTA=1
fi

if grep '^alias e=' ~/.bashrc > /dev/null; then
  echo the e alias is installed
else
  echo "alias e='nano -l'" >> ~/.bashrc
  echo installed the e alias
  DELTA=1
fi

if python3 -c 'import pkgutil; exit(not pkgutil.find_loader("yaml"))'; then
  echo the python3-yaml library is installed
else
  sudo apt install python3-yaml
  echo installed the python3-yaml library
  DELTA=1
fi

if python3 -c 'import pkgutil; exit(not pkgutil.find_loader("vlc"))'; then
  echo the python3-vlc library is installed
else
  sudo apt install python3-vlc
  echo installed the python3-vlc library
  DELTA=1
fi

echo
if [ "${DELTA}" == '1' ]; then
  echo 'changes were made - run ./zero-install.sh again to verify'
  echo 'that all is well.  if it is, you should not see this'
  echo "message again, but rather a 'success' message"
else
  echo 'success - everything looks good'
fi
echo

#============================================================================
# end
#============================================================================
