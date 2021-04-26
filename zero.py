#!/usr/bin/env python3

#==============================================================================
# turn a raspberry pi zero into a wifi relay / sound trigger node compatible
# with the arduino-based relay.ino program.  utilize the external companion
# program 'zero-command.py' to actually effect actions, and monitor its status
# via its text output file 'zero.status'.
#==============================================================================

PROGRAM = 'zero.py'
VERSION = '2.104.251'
CONTACT = 'bright.tiger@gmail.com'

# autostart on boot

from flask import Flask, request
import os, uuid
import socket
from time import sleep

StatusFile = 'zero.status'

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
    # doesn't even have to be reachable
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

def Feedback(Detail=''):
  if Detail:
    Detail = ' - [%s]' % (Detail)
  with open(StatusFile) as f:
    Status = ''.join(f.readlines())
  Html = '%s %s%s\n%s' % (PROGRAM, VERSION, Detail, Status).split('\n')
  Html = '<br>'.join(Html)
  return Html

#==============================================================================
# kick off an asynchronous external process to run the command sequence
#==============================================================================

def RunCommand(Command):
  os.system('/home/pi/git/relay/zero-sequence.py %s &' % (Command))
  sleep(0.2)
  return Feedback(Command)

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
  return RunCommand('+')

@app.route('/off')
def cmd_off():
  return RunCommand('-')

@app.errorhandler(404)
def cmd_sequence(e):
  return RunCommand(request.path[1:])

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=80)

#==============================================================================
# end
#==============================================================================
