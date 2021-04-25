#!/usr/bin/env python3

# autostart on boot
# log mac address and ip
# serve relay logic to gpio
# serve sound logic to alsa device

# plug in sabrent usb audio adapter
#   lsusb -> id 0d8c:0014 C-Media Electronics, Inc. Audio Adapter (Unitek Y247-A)
# speaker-test -c2 --test=wav -w /usr/share/sounds/alsa/Front_Center.wav

from flask import Flask
import os, sys, uuid

MAC = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
print('MAC = [%s]' % (MAC))

os._exit(1)

# return the MAC address of the specified interface

def getMAC(interface='wlan0'):
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
