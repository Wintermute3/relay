#!/usr/bin/env python3

#==============================================================================
# turn a raspberry pi into a gpio sequencer / audio player node compatible
# with the arduino-based relay.ino program.  utilize the external companion
# program 'zero-player.py' to actually effect actions, and monitor its status
# via its text output file 'zero.status'.
#==============================================================================

PROGRAM = 'zero-server.py'
VERSION = '2.104.261'
CONTACT = 'bright.tiger@gmail.com'

# todo: autostart on boot

import os, uuid, socket
from flask import Flask, request
from time import sleep

StatusFile = '/home/pi/git/relay/zero.status'

#==============================================================================
# get the mac address of the active interface
#==============================================================================

def get_mac():
  return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])

#==============================================================================
# get the ip of the interface with the default route
#==============================================================================

def get_ip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    s.connect(('10.255.255.255', 1))
    IP = s.getsockname()[0]
  except Exception:
    IP = '127.0.0.1'
  finally:
    s.close()
  return IP

#==============================================================================
# return the MAC address of the specified interface
#==============================================================================

def getMAC(interface='wlan0'):
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]

#==============================================================================
# report the most recent status posted by the zero-sequence.py utility
#==============================================================================

Counter = 0

def Feedback(Sequence=''):
  if Sequence:
    Sequence = ' [%s]' % (Sequence)
  Retry = 10
  while Retry:
    Retry -= 1
    try:
      with open(StatusFile) as f:
        Status = ''.join(f.readlines())
      Check = int(Status.split('\n')[0])
      if Check == Counter:
        Retry = 0
      else:
        sleep(1)
    except:
      sleep(1)
  Text = '%s %s%s\n%s' % (PROGRAM, VERSION, Sequence, Status)
  return '<br>'.join(Text.split('\n'))

#==============================================================================
# asynchronously kick off zero-sequence.py to run the command sequence
#==============================================================================

def RunSequence(Sequence):
  global Counter
  Counter += 1
  os.system('/home/pi/git/relay/zero-player.py %d %s &' % (Counter, Sequence))
  sleep(0.2)
  return Feedback(Sequence)

#==============================================================================
# main
#==============================================================================

print
print('%s %s' % (PROGRAM, VERSION))
print
print('  mac: %s' % (get_mac()))
print('   ip: %s' % (get_ip ()))
print

app = Flask(__name__)

@app.route('/')
def index():
  return Feedback()

@app.route('/favicon.ico')
def favicon():
  return Feedback()

@app.route('/on')
def cmd_on():
  return RunSequence('+')

@app.route('/off')
def cmd_off():
  return RunSequence('-')

@app.errorhandler(404)
def cmd_sequence(e):
  return RunSequence(request.path[1:])

if __name__ == '__main__':
  #app.run(debug=True, host='0.0.0.0', port=80)
  app.run(host='0.0.0.0', port=80)

#==============================================================================
# end
#==============================================================================
