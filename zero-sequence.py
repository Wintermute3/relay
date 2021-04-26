#!/usr/bin/env python3

#==============================================================================
# execute a sequence of one or more gpio and/or audio output commands
#==============================================================================

PROGRAM = 'zero-sequence.py'
VERSION = '2.104.251'
CONTACT = 'bright.tiger@gmail.com'

#RelayGpio = 23 # pin 16 / for real external relay control
RelayGpio = 47 # pin BCM / built-in activity monitor LED for testing

AudioFile = 'xyz.wav'

StatusFile = 'zero.status'

# plug in sabrent usb audio adapter
#   lsusb -> id 0d8c:0014 C-Media Electronics, Inc. Audio Adapter (Unitek Y247-A)
#
# test left channel:
#   speaker-test -c2 -s1
#
# test right channel:
#   speaker-test -c2 -s2

import os, sys, re
from time import sleep

#==============================================================================
# configure the GPIO output and assure it is initally turned off (raspberry
# pi zero gpios are active low)
#==============================================================================

Relay = None
try:
  from gpiozero import LED
  Relay = LED(RelayGpio, active_high=False, initial_value=False)
except:
  pass

#==============================================================================
# main
#==============================================================================

print
print('%s %s' % (PROGRAM, VERSION))
try:
  Sequence = sys.argv[1]
  print('command: %s' % (Sequence))
  with open(StatusFile, 'w') as f:
    if Relay:
      if Relay.value:
        f.write('relay is on\n')
      else:
        f.write('relay is off\n')
    else:
      f.write('relay undefined\n')
    f.write('sequence: %s\n' % (Sequence))
  for Command in re.split('(\W)', Sequence):
    if Command == '+':
      print('relay on')
      if Relay:
        Relay.on()
    elif Command == '-':
      print('relay off')
      if Relay:
        Relay.off()
    else:
      try:
        Delay = float(Command)
        print('delay %3.1f' % (Delay))
        sleep(Delay)
      except:
        pass
except:
  pass
print

#==============================================================================
# end
#==============================================================================
