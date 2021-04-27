#!/usr/bin/env python3

#==============================================================================
# execute a sequence of one or more gpio and/or audio output commands.  each
# token in a sequence may be one of:
#
#   + . . . . . . . . . turn gpio output on
#   - . . . . . . . . . turn gpio output off
#   * . . . . . . . . . initiate audio playback
#   <integer> . . . . . delay some number of seconds
#
# the gpio output always starts out and ends up in the off state.  audio
# output tokens will be ignored while any previous audio playback is still in
# progress.
#==============================================================================

PROGRAM = 'zero-player.py'
VERSION = '2.104.261'
CONTACT = 'bright.tiger@gmail.com'

# plug in sabrent usb audio adapter
#   lsusb -> id 0d8c:0014 C-Media Electronics, Inc. Audio Adapter (Unitek Y247-A)
#
# test left channel:
#   speaker-test -c2 -s1
#
# test right channel:
#   speaker-test -c2 -s2

import os, sys, re, yaml, time
from syslog import syslog

ConfigFile = '/home/pi/git/relay/zero.config'
StatusFile = '/home/pi/git/relay/zero.status'

print
print('%s %s' % (PROGRAM, VERSION))
print

#==============================================================================
# log a message to the console and /var/log/syslog
#==============================================================================

def Log(Message):
  print('%s' % (Message))
  syslog(Message)

#==============================================================================
# load the yaml configuration file.  it is expected to define RelayGpio and
# AudioFile.
#==============================================================================

try:
  Config = yaml.load(open(ConfigFile), Loader=yaml.FullLoader)
  RelayGpio = Config.RelayGpio
  AudioFile = Config.AudioFile
except:
  Log("*** yaml file '%s' misconfigured or not found!" % (ConfigFile))
  os._exit(1)

#==============================================================================
# configure the GPIO output and assure it is initally turned off (raspberry
# pi zero gpios are active low)
#==============================================================================

Relay = None
try:
  from gpiozero import LED
  Relay = LED(RelayGpio, active_high=False, initial_value=False)
except:
  Log('*** failed to configure gpio %s!' % (RelayGpio))
  os._exit(1)

#==============================================================================
# set up vlc and loop forever waiting for button presses
#==============================================================================

try:
  import vlc
  vlc.Instance("--vout none") # seemed to help select proper output device, not sure why
except:
  Log('*** ERROR 0: python-vlc not found!')
  Log("             try: 'sudo pip3 install python-vlc'")
  os._exit(1)

#==============================================================================
# start audio playback unless still busy with last one
#==============================================================================

def AudioStart(AudioFile):
  try:
    if player.get_state() == 6: # ENDED
      Log('vlc audio playback start')
      player = vlc.MediaPlayer(AudioFile)
      player.play()
    else:
      Log('vlc status %d - skipping start' % (player.get_state()))
  except:
    Log('*** ERROR 3: VLC EXCEPTION')
    Log("             try: 'sudo apt-get install pulseaudio'")

#==============================================================================
# main
#==============================================================================

try:
  Counter = int(sys.argv[1])
  Sequence = sys.argv[2]
  print('sequence [%s]' % (Sequence))
  with open(StatusFile, 'w') as f:
    f.write('%d\n' % (Counter))
    f.write('%s %s [%s]\n' % (PROGRAM, VERSION, Sequence))
    if Relay.value:
      f.write('gpio %d is initially on\n' % (RelayGpio))
    else:
      f.write('gpio %d is initially off\n' % (RelayGpio))
  for Command in re.split('(\W)', Sequence):
    if Command == '+':
      print('gpio %d on' % (RelayGpio))
      Relay.on()
    elif Command == '-':
      print('gpio %d off' % (RelayGpio))
      Relay.off()
    elif Command == '*':
      print("audio '%s' start" % (AudioFile))
      AudioStart(AudioFile)
    else:
      try:
        Delay = int(Command)
        print('delay %d' % (Delay))
        time.sleep(Delay)
      except:
        pass
except:
  pass
print

#==============================================================================
# end
#==============================================================================
