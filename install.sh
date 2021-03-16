#!/bin/bash

#============================================================================
# set things up so that the the relay script is accessible via a shortcut
# from anywhere on the system, and do a couple of other more minor house-
# keeping things.
#============================================================================

# assure we are in the 'pi' user's home directory
cd /home/pi/relay

# whack any references to the nonfunctional syringa repo
if ! grep syringanetworks /etc/hosts > /dev/null; then
  echo '0.0.0.0 mirrors.syringanetworks.net' | sudo tee -a /etc/hosts > /dev/null
fi

# assure nagy's favorite alias is installed
if ! grep 'alias ll=' .bashrc > /dev/null; then
  echo "alias ll='ls -l'" >> .bashrc
fi

# assure the arp-scan utility is installed
if which arp-scan; then
  echo the arp-scan utility is installed
else
  sudo apt install -y arp-scan
fi

# install the relay shortcut script on the path
sudo cp relay /usr/local/sbin/
echo the relay helper script is installed

#============================================================================
# end
#============================================================================
