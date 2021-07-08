#!/bin/bash

PROGRAM='pi-install.sh'
VERSION='2.107.071'
CONTACT='bright.tiger@mail.com' # michael nagy

#============================================================================
# set up a raspberry pi in either orchestrator or player mode as selected
# by the command-line parameter, or a pi zero in player mode
#
# in orchestrator mode, set things up so that the the relay script is
# accessible via a shortcut from anywhere on the system, and do a couple
# of other house-keeping things
#
# in player mode, set things up so that the pulseaudio and player services
# autostart on boot, and do a couple of other house-keeping things
#============================================================================

echo
echo "${PROGRAM} ${VERSION}"
echo

#============================================================================
# verify command-line option for raspberry pi or pi zero
#============================================================================

TARGET="${1}"
if [ -z "${TARGET}" ]; then
  echo "*** expected 'player' or 'orchestrator' option!"
  echo
  exit 1
else
  if cat /proc/cpuinfo | grep 'Pi Zero' > /dev/null; then
    PITYPE='pizero'
    if [ "${TARGET}" != 'player' ]; then
      echo "*** expected 'player' option!"
      echo # pi zero can only be a player
      exit 1
    fi
  else
    PITYPE='raspberrypi'
    if [ "${TARGET}" != 'player' -a "${TARGET}" != 'orchestrator' ]; then
      echo "*** expected 'player' or 'orchestrator' option!"
      echo # raspberry pi can be player or orchestrator
      exit 1
    fi
  fi
fi

#============================================================================
# DELTA gets set to 1 if anything is changed during installation
#============================================================================

DELTA=0

#============================================================================
# remove the specified systemd service
#============================================================================

function RemoveSystemd {
  SERVICE=${1}
  if [ -f /etc/systemd/system/${SERVICE}.service ]; then
    echo "stopping and disabling the systemd ${SERVICE} service..."
    sudo systemctl stop ${SERVICE}
    sudo systemctl disable ${SERVICE}
    echo "  stopped and disabled the systemd ${SERVICE} service"
    sudo rm /etc/systemd/system/${SERVICE}.service
    DELTA=1
  else
    echo "the systemd service ${SERVICE} is not installed"
  fi
}

#============================================================================
# assure the specified systemd service is current, running and enabled
#============================================================================

function AssureSystemd {
  SERVICE=${1}
  if [ -f /etc/systemd/system/${SERVICE}.service ]; then
    if cmp -s ${SERVICE}.service /etc/systemd/system/${SERVICE}.service; then
      if systemctl -q is-active ${SERVICE}; then
        echo "the systemd service ${SERVICE} is running"
      else
        echo "starting and enabling the systemd ${SERVICE} service..."
        sudo systemctl daemon-reload
        sudo systemctl start ${SERVICE}
        sudo systemctl enable ${SERVICE}
        echo "  started and enabled the systemd ${SERVICE} service"
        DELTA=1
      fi
    else
      echo "reinstalling the systemd ${SERVICE} service..."
      sudo systemctl disable ${SERVICE}
      sudo systemctl stop    ${SERVICE}
      sudo cp ${SERVICE}.service /etc/systemd/system/
      sudo systemctl daemon-reload
      sudo systemctl start ${SERVICE}
      sudo systemctl enable ${SERVICE}
      echo "  reinstalling the systemd ${SERVICE} service"
      DELTA=1
    fi
  else
    echo "installing the systemd ${SERVICE} service..."
    sudo cp ${SERVICE}.service /etc/systemd/system/
    sudo systemctl start ${SERVICE}
    sudo systemctl enable ${SERVICE}
    echo "  installed the systemd ${SERVICE} service"
    DELTA=1
  fi
}

#============================================================================
# assure the specified python3 library is installed
#============================================================================

function AssurePythonLib() {
  LIBRARY=${1}
  if python3 -c "import pkgutil; exit(not pkgutil.find_loader(\"${LIBRARY}\"))"; then
    echo "the python3-${LIBRARY} library is installed"
  else
    echo "installing the python3-${LIBRARY} library..."
    sudo apt install python3-${LIBRARY}
    echo "  installed the python3-${LIBRARY} library"
    DELTA=1
  fi
}

#============================================================================
# assure we are in the 'pi' user's home directory
#============================================================================

cd /home/pi/relay

#============================================================================
# whack any references to the nonfunctional syringa repo
#============================================================================

if grep syringanetworks /etc/hosts > /dev/null; then
  echo the syringa workaround is installed
else
  echo -e '0.0.0.0\t\tmirrors.syringanetworks.net' | sudo tee -a /etc/hosts > /dev/null
  echo installed the syringa workaround
  DELTA=1
fi

#============================================================================
# assure nagy's favorite aliases are installed
#============================================================================

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

#============================================================================
# orchestrator mode
#============================================================================

if [ "${TARGET}" == 'orchestrator' ]; then

  #============================================================================
  # assure the arp-scan utility is installed
  #============================================================================

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

  #============================================================================
  # install the relay shortcut script on the path
  #============================================================================

  if [ -f /usr/local/bin/relay ]; then
    echo the relay helper script is installed
  else
    sudo cp relay /usr/local/bin/
    echo installed the relay helper script
    DELTA=1
  fi

  #============================================================================
  # initialize the relay.json file if it doesn't already exist
  #============================================================================

  if [ -f relay.json ]; then
    echo the relay.json file already exists
  else
    cp relay.default relay.json
    echo initialized the relay.json file
    DELTA=1
  fi
fi

#============================================================================
# player mode
#============================================================================

if [ "${TARGET}" == 'player' ]; then

  #============================================================================
  # assure the yaml and vlc python3 libraries are installed
  #============================================================================

  AssurePythonLib yaml
  AssurePythonLib vlc

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
    DELTA=1
  fi

  #============================================================================
  # assure required systemd services are installed, enabled and running
  #============================================================================

  # old stuff
  RemoveSystemd zero
  RemoveSystemd pulse

  # new stuff
  AssureSystemd pulseaudio
  AssureSystemd pi-player

  #============================================================================
  # create the pi-player.config file from the default if necessary
  #============================================================================

  if [ -f pi-player.config ]; then
    echo 'the pi-player.config file already exists'
  else
    echo 'creating the pi-player.config file...'
    cat << EOF > pi-player.config
#==============================================================================
# PROGRAM = 'pi-player.config'
# VERSION = '2.107.071'
# CONTACT = 'bright.tiger@gmail.com'
#
# note: this file was copied from 'pi-player.default' on installation if
#       it did not already exist.  make any edits in this copy, not to the
#       original 'pi-player.default', file to avoid conflicts with git pull
EOF
    tail -n +9 pi-player.default >> pi-player.config
    echo '  created the pi-player.config file'
    DELTA=1
  fi
fi

#============================================================================
# report and exit
#============================================================================

echo
if [ "${DELTA}" == '1' ]; then
  echo "changes were made - run './${PROGRAM} ${TARGET}' again to verify"
  echo 'that all is well.  if it is, you should not see this'
  echo "message again, but rather a 'success' message"
else
  echo 'success - everything looks good'
fi
echo

#============================================================================
# end
#============================================================================
