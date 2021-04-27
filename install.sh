#!/bin/bash

PROGRAM='install.sh'
VERSION='2.104.271'
CONTACT='bright.tiger@mail.com' # michael nagy

#============================================================================
# set things up so that the the relay script is accessible via a shortcut
# from anywhere on the system, and do a couple of other more minor house-
# keeping things.
#============================================================================

echo

# assure we are in the 'pi' user's home directory
cd /home/pi/relay

DELTA=0

# whack any references to the nonfunctional syringa repo
if grep syringanetworks /etc/hosts > /dev/null; then
  echo the syringa workaround is installed
else
  echo -e '0.0.0.0\t\tmirrors.syringanetworks.net' | sudo tee -a /etc/hosts > /dev/null
  echo installed the syringa workaround
  DELTA=1
fi

# assure nagy's favorite alias is installed
if grep '^alias ll=' ~/.bashrc > /dev/null; then
  echo the ll alias is installed
else
  echo "alias ll='ls -lh'" >> ~/.bashrc
  echo installed the ll alias
  DELTA=1
fi

# assure the arp-scan utility is installed
if which arp-scan > /dev/null; then
  echo the arp-scan utility is installed
else
  echo
  echo installing the arp-scan utility...
  echo
  sudo apt install -y arp-scan
  echo
  echo installed the arp-scan utility
  DELTA=1
fi

# install the relay shortcut script on the path
if [ -f /usr/local/bin/relay ]; then
  echo the relay helper script is installed
else
  sudo cp relay /usr/local/bin/
  echo installed the relay helper script
  DELTA=1
fi

echo
if [ "${DELTA}" == '1' ]; then
  echo 'changes were made - run ./install.sh again to verify'
  echo 'that all is well.  if it is, you should not see this'
  echo "message again, but rather a 'success' message"
else
  echo 'success - everything looks good'
fi
echo

#============================================================================
# end
#============================================================================
