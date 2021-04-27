#!/bin/bash

PROGRAM='zero-install.sh'
VERSION='2.104.271'
CONTACT='bright.tiger@mail.com' # michael nagy

#============================================================================
# set things up so that zero-server.py autostarts on boot and do a couple
# of other more minor house-keeping things.
#============================================================================

echo

if ! cat /proc/cpuinfo | grep 'Pi Zero' > /dev/null; then
  echo '*** this installer expects to be run on a pi zero!'
  echo
  exit 1
fi

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

# assure the systemd service is current, running and enabled
if [ -f /etc/systemd/system/zero.service ]; then
  if cmp -s zero.service /etc/systemd/system/zero.service; then
    echo systemd service is current
    if systemctl status zero; then
      echo systemd service is running
    else
      echo starting and enabling systemd service
      sudo systemctl daemon-reload
      sudo systemctl start zero
      sudo systemctl enable zero
      DELTA=1
    fi
  else
    echo reinstalling systemd service
    sudo systemctl disable zero
    sudo systemctl stop    zero
    sudo cp zero.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl start zero
    sudo systemctl enable zero
    DELTA=1
  fi
else
  echo installing systemd service
  sudo cp zero.service /etc/systemd/system/
  sudo systemctl start zero
  sudo systemctl enable zero
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
