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
VERSION = '2.104.271'
CONTACT = 'bright.tiger@gmail.com'

# plug in sabrent usb audio adapter
#   lsusb -> id 0d8c:0014 C-Media Electronics, Inc. Audio Adapter (Unitek Y247-A)
#
# test left channel:
#   speaker-test -c2 -s1
#
# test right channel:
#   speaker-test -c2 -s2

import os, sys, re, time
from syslog import syslog

ConfigFile = '/home/pi/relay/zero.config'
StatusFile = '/home/pi/relay/zero.status'

#==============================================================================
# log a message to the console and /var/log/syslog
#==============================================================================

def Log(Message):
  print('%s' % (Message))
  syslog(Message)

print
Log('%s %s' % (PROGRAM, VERSION))
print

#==============================================================================
# load the yaml configuration file.  it is expected to define RelayGpio and
# AudioFile.
#==============================================================================

try:
  import yaml
except:
  Log('*** ERROR 0: import yaml failed!')
  Log("             try: 'sudo apt install python3-yaml'")
  os._exit(1)

try:
  Config = yaml.load(open(ConfigFile))
  RelayGpio = Config['RelayGpio']
  AudioFile = Config['AudioFile']
except:
  Log("*** ERROR 1: yaml file '%s' misconfigured or not found!" % (ConfigFile))
  os._exit(1)

#==============================================================================
# configure the GPIO output and assure it is initally turned off (raspberry
# pi zero gpios are active low)
#==============================================================================

Relay = None
try:
  from gpiozero import LED
  Relay = LED(RelayGpio, active_high=False, initial_value=True)
except:
  Log('*** ERROR 2: failed to configure gpio %s!' % (RelayGpio))
  os._exit(1)

#==============================================================================
# set up vlc and loop forever waiting for button presses
#==============================================================================

try:
  import vlc
  vlc.Instance("--vout none") # seemed to help select proper output device, not sure why
except:
  Log('*** ERROR 3: import vlc failed!')
  Log("             try: 'sudo apt install python3-vlc'")
  os._exit(1)

#==============================================================================
# start playing audiofile unless still busy with last one.  if called with no
# audiofile and a previous playback is still in progress, wait for it to
# finish before returning (exit processing)
#==============================================================================

VlcPlayer = None

def AudioPlayback(AudioFile=None):
  global VlcPlayer
  try:
    if AudioFile:
      if VlcPlayer:
        if VlcPlayer.get_state() != 6: # ENDED
          Log('vlc audio playback busy / skipped')
          return
      Log('vlc audio playback start')
      VlcPlayer = vlc.MediaPlayer(AudioFile)
      VlcPlayer.play()
    else:
      if VlcPlayer:
        if VlcPlayer.get_state() != 6: # ENDED
          Log('vlc audio playback in progress')
          while VlcPlayer.get_state() != 6: # ENDED
            time.sleep(0.5)
          Log('vlc audio playback complete')
  except:
    Log('*** ERROR 4: vlc exception!')
    Log("             try: 'sudo apt install pulseaudio'")

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
      Log('gpio %d on' % (RelayGpio))
      Relay.off()
    elif Command == '-':
      Log('gpio %d off' % (RelayGpio))
      Relay.on()
    elif Command == '*':
      Log("audio '%s' start" % (AudioFile))
      AudioPlayback(AudioFile)
    else:
      try:
        Delay = int(Command)
        print('delay %d' % (Delay))
        time.sleep(Delay)
      except:
        pass
except:
  pass
AudioPlayback()
print

#==============================================================================
# end
#==============================================================================
