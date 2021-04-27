#!/usr/bin/env python3

#todo: handle fractional seconds delay
#todo: handle audio trigger

#==============================================================================
# execute a sequence of one or more gpio and/or audio output commands
#==============================================================================

PROGRAM = 'zero-player.py'
VERSION = '2.104.261'
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
  pass # allow limited testing on non-pi-zero platforms

#==============================================================================
# main
#==============================================================================

print
print('%s %s' % (PROGRAM, VERSION))
try:
  Counter = int(sys.argv[1])
  Sequence = sys.argv[2]
  print('sequence [%s]' % (Sequence))
  with open(StatusFile, 'w') as f:
    f.write('%d\n' % (Counter))
    f.write('%s %s [%s]\n' % (PROGRAM, VERSION, Sequence))
    if Relay: # allow limited testing on non-pi-zero platforms
      if Relay.value:
        f.write('gpio %d is initially on\n' % (RelayGpio))
      else:
        f.write('gpio %d is initially off\n' % (RelayGpio))
    else:
      f.write('gpio %d undefined\n' % (RelayGpio))
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
