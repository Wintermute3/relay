#!/usr/bin/env python3

#==============================================================================
# this program looks up wifi relays on the same subnet as the host where it
# is running by mac address and sends on/off commands to them using curl.  it
# is configured (mac/name mappings) using the relay.json file, which should
# be present next to this file.
#==============================================================================

PROGRAM = 'relay.py'
VERSION = '2.103.041'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, subprocess, json

#------------------------------------------------------------------------------
# announce ourselves
#------------------------------------------------------------------------------

def Splash():
  print()
  print("%s %s" % (PROGRAM, VERSION))
  print()

#------------------------------------------------------------------------------
# the mac/name mapping json configuration file
#------------------------------------------------------------------------------

JsonFile = '%s.json' % (PROGRAM.split('.')[0])

#------------------------------------------------------------------------------
# show usage help
#------------------------------------------------------------------------------

def ShowHelp():
  HelpText = '''\
    this program controls wifi relays

usage:

    %s [-h] [-d] command {command {command...}}

where:

    -h . . . . . . this help text
    -d . . . . . . enable debug output
    command  . . . command, as listed below (repeat as desired)

commands may be:

    {name}+ . . . . . . turn relay {name} on
    {name}- . . . . . . turn relay {name} off

names must be configured in the %s file
'''
  Splash()
  print(HelpText % (sys.argv[0], JsonFile))
  os._exit(1)

#------------------------------------------------------------------------------
# error exit
#------------------------------------------------------------------------------

def ShowError(Message):
  print('*** %s!' % (Message))
  print('*** try -h for help!')
  print()
  os._exit(1)

#------------------------------------------------------------------------------
# load the json configuration file and do a quick validation
#------------------------------------------------------------------------------

try:
  Relays = json.load(open(JsonFile))
  try:
    for Relay in Relays['relay']:
      Relay['mac' ] = Relay['mac' ].lower()
      Relay['name'] = Relay['name'].lower()
      Relay['hit' ] = False
  except:
    ShowError("configuration file '%s' is structured improperly" % (JsonFile))
except:
  ShowError("configuration file '%s' is misformatted" % (JsonFile))

if not len(Relays):
  ShowError("configuration file '%s' defines no relays" % (JsonFile))

#------------------------------------------------------------------------------
# validate the argument list and build a command list
#------------------------------------------------------------------------------

RelayCommands = []
DebugFlag = len(sys.argv) < 2

for arg in sys.argv[1:]:
  if arg == '-h':
    ShowHelp()
  if arg == '-d':
    DebugFlag = True
  else:
    ArgCommand = arg.lower()
    Hit = False
    for Relay in Relays['relay']:
      Name = Relay['name']
      Mac  = Relay['mac' ]
      On  = '%s+' % (Name)
      Off = '%s-' % (Name)
      if ArgCommand == On:
        RelayCommands.append({'name': Name, 'mac': Mac, 'ip': None, 'command': 'on'})
        Hit = True
      elif ArgCommand == Off:
        RelayCommands.append({'name': Name, 'mac': Mac, 'ip': None, 'command': 'off'})
        Hit = True
    if not Hit:
      ShowError("relay command '%s' not recognized - check '%s' file" % (arg, JsonFile))

#------------------------------------------------------------------------------
# with at least one seemingly valid command requested, see if we can match it
# to an active relay on the network and issue it
#------------------------------------------------------------------------------

if DebugFlag:
  Splash()

try:
  Hits = 0
  Handled = []
  if DebugFlag:
    print('  arp-scan:')
  for Line in subprocess.check_output(['sudo', 'arp-scan', '-l', '-q']).decode('ascii').split('\n'):
    if DebugFlag:
      print('    %s' % (Line))
    if not Line in Handled:
      Handled.append(Line)
      try:
        if Line[0] in '123456789' and ':' in Line:
          IpAddress, MacAddress = Line.split('\t')
          MacAddress = MacAddress.lower()
          for Relay in Relays['relay']:
            if Relay['mac'] == MacAddress:
              Relay['hit'] = True
          for Relay in RelayCommands:
            if Relay['mac'] == MacAddress:
              Relay['ip'] = IpAddress
              if DebugFlag:
                print('  relay name: %s, mac: %s, ip: %s, cmd: %s' % (
                  Relay['name'], MacAddress, IpAddress, Relay['command']))
              Hits += 1
      except:
        pass
  if Hits:
    if len(RelayCommands):
      for Command in RelayCommands:
        URL = 'http://%s/%s' % (Command['ip'], Command['command'])
        if DebugFlag:
          print('curl -s %s' % (URL))
        for Line in subprocess.check_output(['curl','-s',URL]).decode('ascii').split('\n'):
          if DebugFlag:
            print('>> [%s]' % (Line.strip()))
    else:
      ShowError("no relays from configuration file '%s' found" % (JsonFile))
  if DebugFlag:
    for Relay in Relays['relay']:
      if Relay['hit']:
        Status = '     online'
      else:
        Status = '*** offline'
      print('  name: %s, mac: %s  %s' % (Relay['name'], Relay['mac'], Status))
    print()
except:
  ShowError("install the 'arp-scan' utility and try again")

#==============================================================================
# end
#==============================================================================
