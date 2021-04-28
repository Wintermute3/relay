#!/bin/bash

PROGRAM='zero-install.sh'
VERSION='2.104.271'
CONTACT='bright.tiger@mail.com' # michael nagy

#============================================================================
# set things up so that pulseaudio and zero-server autostart on boot and
# do a couple of other house-keeping things
#============================================================================

echo
if ! cat /proc/cpuinfo | grep 'Pi Zero' > /dev/null; then
  echo '*** this installer expects to be run on a pi zero!'
  echo
  exit 1
fi

#============================================================================
# DELTA gets set to 1 if anything is changed during installation
#============================================================================

DELTA=0

#============================================================================
# assure the specified systemd service is current, running and enabled
#============================================================================

function AssureSystemd {
  SERVICE=${1}
  if [ -f /etc/systemd/system/${SERVICE}.service ]; then
    if cmp -s ${SERVICE}.service /etc/systemd/system/${SERVICE}.service; then
      if systemctl -q is-active ${SERVICE}; then
        echo 'systemd service ${SERVICE} is running'
      else
        echo 'starting and enabling the systemd ${SERVICE} service...'
        sudo systemctl daemon-reload
        sudo systemctl start ${SERVICE}
        sudo systemctl enable ${SERVICE}
        echo '  started and enabled the systemd ${SERVICE} service'
        DELTA=1
      fi
    else
      echo 'reinstalling the systemd ${SERVICE} service...'
      sudo systemctl disable ${SERVICE}
      sudo systemctl stop    ${SERVICE}
      sudo cp ${SERVICE}.service /etc/systemd/system/
      sudo systemctl daemon-reload
      sudo systemctl start ${SERVICE}
      sudo systemctl enable ${SERVICE}
      echo '  reinstalling the systemd ${SERVICE} service'
      DELTA=1
    fi
  else
    echo 'installing the systemd ${SERVICE} service...'
    sudo cp ${SERVICE}.service /etc/systemd/system/
    sudo systemctl start ${SERVICE}
    sudo systemctl enable ${SERVICE}
    echo '  installed the systemd ${SERVICE} service'
    DELTA=1
  fi
}

#============================================================================
# assure we are in the 'pi' user's home directory
#============================================================================

cd /home/pi/relay

#============================================================================
# assure nagy's favorite aliases are installed
#============================================================================

if grep '^alias ll=' ~/.bashrc > /dev/null; then
  echo 'the ll alias is installed'
else
  echo 'installing the ll alias...'
  echo "alias ll='ls -lh'" >> ~/.bashrc
  echo '  installed the ll alias'
  DELTA=1
fi

if grep '^alias e=' ~/.bashrc > /dev/null; then
  echo 'the e alias is installed'
else
  echo 'installing the e alias...'
  echo "alias e='nano -l'" >> ~/.bashrc
  echo '  installed the e alias'
  DELTA=1
fi

#============================================================================
# assure the yaml and vlc python3 libraries are installed
#============================================================================

if python3 -c 'import pkgutil; exit(not pkgutil.find_loader("yaml"))'; then
  echo 'the python3-yaml library is installed'
else
  echo 'installing the python3-yaml library...'
  sudo apt install python3-yaml
  echo '  installed the python3-yaml library'
  DELTA=1
fi

if python3 -c 'import pkgutil; exit(not pkgutil.find_loader("vlc"))'; then
  echo 'the python3-vlc library is installed'
else
  echo 'installing the python3-vlc library...'
  sudo apt install python3-vlc
  echo '  installed the python3-vlc library'
  DELTA=1
fi

#============================================================================
# assure pulseaudio is configured for anonymous authentication
#============================================================================

PULSECONFIG=/etc/pulse/system.pa
PULSETARGET='auth-anonymous=1'
PULSEMODULE='load-module module-native-protocol-unix'

if grep -q ${PULSETARGET} ${PULSECONFIG} ; then
  echo 'pulseaudio is configured for anonymous authentication'
else
  echo 'configuring pulseaudio for anonymous authentication...'
  sudo sed -i "s/${PULSEMODULE}/${PULSEMODULE} ${PULSETARGET}/" ${PULSECONFIG}
  echo '  configured pulseaudio for anonymous authentication'
fi

#============================================================================
# assure required systemd services are installed, enabled and running
#============================================================================

AssureSystemd pulse
AssureSystemd zero

#============================================================================
# report and exit
#============================================================================

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
