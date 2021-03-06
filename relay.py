#!/usr/bin/env python3

#==============================================================================
# this program looks up player clients on the same subnet as the host where it
# is running by mac address and sends commands to them using curl.  it is
# configured (mac/name mappings) using the relay.json file, which should be
# present next to this file.
#==============================================================================

PROGRAM = 'relay.py'
VERSION = '2.107.071'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, subprocess, json, shutil

NameMap   = False # set with -n on command-line
DebugFlag = False # set with -d on command-line
ForceScan = False # set with -f on command-line

#------------------------------------------------------------------------------
# announce ourselves
#------------------------------------------------------------------------------

def Splash():
  print()
  print("%s %s" % (PROGRAM, VERSION))
  print()

#------------------------------------------------------------------------------
# the mac/name mapping json configuration file (default and runtime), and the
# arp-scan cache file
#------------------------------------------------------------------------------

DefaultFile = '%s.default' % (PROGRAM.split('.')[0])

JsonFile = '%s.json' % (PROGRAM.split('.')[0])
PeerFile = '%s.peer' % (PROGRAM.split('.')[0])

#------------------------------------------------------------------------------
# show usage help
#------------------------------------------------------------------------------

def ShowHelp():
  HelpText = '''\
    this program controls wifi relays and audio playback

usage:

    %s [-h] [-n] [-d] [-f] command {command {command...}}

where:

    -h . . . . . . this help text
    -n . . . . . . show name to mac mapping table status
    -d . . . . . . enable debug output
    -f . . . . . . force arp-scan cache update

    command  . . . command, as listed below (repeat as desired)

commands may be:

    {name}@ . . . . . . play audio track (not on nodemcu)
    {name}%% . . . . . . abort audio playback (not on nodemcu)
    {name}+ . . . . . . turn relay {name} on
    {name}- . . . . . . turn relay {name} off

you may also follow {name} with a sequence of @/%%/+/- and delay times in
seconds, so for instance the following will turn relay 'a1' off (which
may be its initial state anyway), delay two seconds, turn it on, play
an audio track, delay another 10 seconds, and turn it off again:

    a1-2+@10-

command sequences must always start with either @, + or -, and names
must be configured in the %s file.  arp-scan results will be
cached in the %s file.
'''
  Splash()
  print(HelpText % (sys.argv[0], JsonFile, PeerFile))
  os._exit(1)

#------------------------------------------------------------------------------
# warning / error exit
#------------------------------------------------------------------------------

def ShowMessage(Message):
  print('*** %s!' % (Message))

def ShowInfo(Message):
  ShowMessage('info: %s' % (Message))

def ShowError(Message):
  ShowMessage('error: %s' % (Message))
  print('*** try -h for help!')
  print()
  os._exit(1)

#------------------------------------------------------------------------------
# load the json configuration file and do a quick validation (defaulting it
# if it doesn't already exist)
#------------------------------------------------------------------------------

if not os.path.exists(JsonFile):
  shutil.copy(DefaultFile, JsonFile)

try:
  Relays = json.load(open(JsonFile))
  try:
    Macs = []
    for Relay in Relays['relay']:
      Mac  = Relay['mac' ].lower()
      Name = Relay['name'].lower()
      Relay['mac' ] = Mac
      Relay['name'] = Name
      Relay['hit' ] = False
      if Mac in Macs:
        ShowInfo("configuration file '%s' defines mac '%s' multiple times" % (JsonFile, Mac))
      Macs.append(Mac)
  except:
    ShowError("configuration file '%s' is structured improperly" % (JsonFile))
except:
  ShowError("configuration file '%s' is misformatted" % (JsonFile))

if not len(Relays):
  ShowError("configuration file '%s' defines no relays" % (JsonFile))

#------------------------------------------------------------------------------
# load the json arp-scan cache file and do a quick validation
#------------------------------------------------------------------------------

try:
  Peers = json.load(open(PeerFile))
  try:
    for Peer in Peers['peers']:
      IpV4 = Peer['ip' ].lower()
      Mac  = Peer['mac'].lower()
    if DebugFlag:
      print("  loaded '%s' (%d peers)" % (PeerFile, len(Peers['peers'])))
  except:
    ShowError("arp-scan cache file '%s' is structured improperly" % (PeerFile))
    Peers = None
except:
  Peers = None

#------------------------------------------------------------------------------
# return true if the command string is valid
#------------------------------------------------------------------------------

def ValidCommand(Command):
  while Command and Command[0] in '0123456789+-@%':
    Command = Command[1:] # skip valid characters
  if Command:
    return False # stuck on invalid character
  return True # all characters are valid

#------------------------------------------------------------------------------
# validate the argument list and build a command list.  each command token may
# look like this:
#
#    {relayid}(@|%|+|-)[<time>|@|%|+|-]
#
# the items in the square brackets may be repeated as desired.  for instance,
# to turn on relay a1, wait 30 seconds, and then turn it off:
#
#    a1+30-
#
# if relay a1 is already off and you want to wait 120 seconds to turn it on,
# then wait another 30 seconds to turn it off, then:
#
#    a1-120+30-
#------------------------------------------------------------------------------

RelayCommands = []

for arg in sys.argv[1:]:
  if arg == '-h':
    ShowHelp()
  elif arg == '-d':
    DebugFlag = True
  elif arg == '-f':
    ForceScan = True
  elif arg == '-n':
    NameMap = True
  else:
    ArgCommand = arg.lower()
    Hit = False
    for Relay in Relays['relay']:
      Name = Relay['name']
      Mac  = Relay['mac' ]
      if ArgCommand.startswith(Name):
        Command = ArgCommand[len(Name):]
        if ValidCommand(Command):
          RelayCommands.append({'name': Name, 'mac': Mac, 'ip': None, 'command': Command})
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

  # if we loaded a peers file, use those mappings to find the ip
  # addresses of configured relays by matching mac addresses

  if DebugFlag:
    print('$peers')
  if Peers:
    if DebugFlag:
      print('  cache load:')
    for Peer in Peers['peers']:
      if DebugFlag:
        print('    %s' % (Peer))
      for Relay in Relays['relay']:
        if Relay['mac'] == Peer['mac']:
          Relay['hit'] = True
      for Relay in RelayCommands:
        if Relay['mac'] == Peer['mac']:
          Relay['ip'] = Peer['ip']
          if DebugFlag:
            print('  relay name: %s, mac: %s, ip: %s, cmd: %s' % (
              Relay['name'], Relay['mac'], Relay['ip'], Relay['command']))
          Hits += 1

  # if we didn't find a peers file, or if the -f command-line option was
  # specified, do an arp-scan and merge the result into the peers file

  if DebugFlag:
    print('$arp-scan')
  if ForceScan or not Peers:
    if DebugFlag:
      print('  arp-scan:')
    if not Peers:
      Peers = {'peers': []}
    if DebugFlag:
      print('  starting with %d peers' % (len(Peers['peers'])))
    for Line in subprocess.check_output(['sudo', 'arp-scan', '-l', '-q']).decode('ascii').split('\n'):
      if DebugFlag:
        print('    %s' % (Line))
      if Line and not Line in Handled:
        Handled.append(Line)
        try:
          if Line[0] in '123456789' and ':' in Line:
            IpAddress, MacAddress = Line.split('\t')
            MacAddress = MacAddress.lower()
            Hit = False
            for Peer in Peers['peers']:
              if Peer['mac'] == MacAddress:
                Hit = True
                if Peer['ip'] != IpAddress:
                  Peer['ip'] = IpAddress
                  if DebugFlag:
                    print('  updated mac %s to ip %s' % (MacAddress, IpAddress))
            if not Hit:
              Peers['peers'].append({'ip': IpAddress, 'mac': MacAddress})
              print('  appended mac %s as ip %s' % (MacAddress, IpAddress))
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
    with open(PeerFile, 'w') as f:
      f.write(json.dumps(Peers, indent=2))
      if DebugFlag:
        print('  ending with %d peers' % (len(Peers['peers'])))
        print("  wrote '%s'" % (PeerFile))

  # if we managed to map at least one relay to an ip address, either
  # via an arp-scan run or from the cached peers file, issue its
  # commands using curl

  if DebugFlag:
    print('$hits')
  if Hits:
    if len(RelayCommands):
      for Command in RelayCommands:
        URL = 'http://%s/%s' % (Command['ip'], Command['command'])
        if DebugFlag:
          print('curl -s %s' % (URL))
        try:
          for Line in subprocess.check_output(['curl','-s',URL]).decode('ascii').split('\n'):
            if DebugFlag:
              print('>> [%s]' % (Line.strip()))
        except:
          ShowError("curl failed to %s" % (Command['ip']))
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

if NameMap:
  List = []
  NameWidth = 4
  for Relay in Relays['relay']:
    Name = Relay['name']
    NameWidth = max(NameWidth, len(Name))
  print()
  print('  %*s  mac               ip'              % (NameWidth, 'name'))
  print( '  %s  ----------------- ---------------' % ('-' * NameWidth  ))
  for Relay in Relays['relay']:
    Name = Relay['name']
    Mac  = Relay['mac']
    if 'ip' in Relay:
      Ip = Relay['ip']
    else:
      Ip = ''
    List.append('%*s  %17s  %s' % (NameWidth, Name, Mac, Ip))
  for Item in sorted(List):
    print('  %s' % (Item))
  List = []
  for Peer in Peers['peers']:
    Mac = Peer['mac']
    Ip  = Peer['ip' ]
    Hit = False
    for Relay in Relays['relay']:
      if Mac == Relay['mac']:
        Hit = True
    if not Hit:
      List.append('%*s  %17s  %s' % (NameWidth, '', Mac, Ip))
  print( '  %s  ----------------- ---------------' % ('-' * NameWidth  ))
  for Item in sorted(List):
    print('  %s' % (Item))
  print()

#==============================================================================
# end
#==============================================================================
