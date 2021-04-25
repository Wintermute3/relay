#!/usr/bin/env python3

#==============================================================================
# turn a raspberry pi zero into a wifi relay / sound trigger node compatible
# with the arduino-based relay.ino program
#==============================================================================

PROGRAM = 'zero.py'
VERSION = '2.104.241'
CONTACT = 'bright.tiger@gmail.com'

RelayPin = 23 # pin 16

# autostart on boot
# log mac address and ip
# serve relay logic to gpio
# serve sound logic to alsa device

# plug in sabrent usb audio adapter
#   lsusb -> id 0d8c:0014 C-Media Electronics, Inc. Audio Adapter (Unitek Y247-A)
#
# test left channel:
#   speaker-test -c2 -s1
#
# test right channel:
#   speaker-test -c2 -s2

from flask import Flask, request
import os, sys, uuid
import socket
from gpiozero import LED
from time import sleep
import asyncio

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

#==============================================================================
# configure the GPIO output and assure it is initally turned off
#==============================================================================

Relay = LED(RelayPin, active_high=True, initial_value=False)

#==============================================================================
# kick off an asynchronous external process to run the command string
#==============================================================================

def RunCommand(Command):
  proc = await asyncio.create_subprocess_exec(
      'zero-gpio.py', RelayPin, Command)
  proc = await asyncio.create_subprocess_exec(
      'zero-audio.py', RelayPin, Command)
  #,
  #    stdout=asyncio.subprocess.PIPE,
  #    stderr=asyncio.subprocess.PIPE)

# do something else while ls is working

# if proc takes very long to complete, the CPUs are free to use cycles for
# other processes
#stdout, stderr = await proc.communicate()

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

def Feedback(Detail=''):
  if Detail:
    Detail = ' [%s]' % (Detail)
  if Relay.value:
    Status = 'on'
  else:
    Status = 'off'
  return '%s %s - relay is %s%s' % (PROGRAM, VERSION, Status, Detail)

@app.route('/')
def index():
  return Feedback()

@app.route('/on')
def cmd_on():
  Relay.on()
  return Feedback()

@app.route('/off')
def cmd_off():
  Relay.off()
  return Feedback()

@app.errorhandler(404)
def cmd_sequence(e):
  Command = request.path[1:]
  return Feedback(Command)

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=80)

#==============================================================================
# end
#==============================================================================
