#!/bin/bash

PROGRAM='pi-uninstall.sh'
VERSION='2.107.071'
CONTACT='bright.tiger@mail.com' # michael nagy

#============================================================================
# uninstall systemd services and shortcuts previously installed by
# the `pi-install.sh` script
#============================================================================

echo
echo "${PROGRAM} ${VERSION}"
echo

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
# assure we are in the 'pi' user's home directory
#============================================================================

cd /home/pi/relay

#============================================================================
# uninstall the relay shortcut script on the path
#============================================================================

if [ -f /usr/local/bin/relay ]; then
  sudo rm /usr/local/bin/relay
  echo uninstalled the relay helper script
  DELTA=1
else
  echo the relay helper script is not installed
fi

#============================================================================
# assure systemd services are stopped and disabled
#============================================================================

# old stuff
RemoveSystemd zero
RemoveSystemd pulse

# new stuff
RemoveSystemd pulseaudio
RemoveSystemd pi-player

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
