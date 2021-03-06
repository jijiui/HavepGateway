# BLE iBeaconScanner based on https://github.com/adamf/BLE/blob/master/ble-scanner.py
# JCS 06/07/14

DEBUG = False
# DEBUG = True
# BLE scanner based on https://github.com/adamf/BLE/blob/master/ble-scanner.py
# BLE scanner, based on https://code.google.com/p/pybluez/source/browse/trunk/examples/advanced/inquiry-with-rssi.py

# https://github.com/pauloborges/bluez/blob/master/tools/hcitool.c for lescan
# https://kernel.googlesource.com/pub/scm/bluetooth/bluez/+/5.6/lib/hci.h for opcodes
# https://github.com/pauloborges/bluez/blob/master/lib/hci.c#L2782 for functions used by lescan

# performs a simple device inquiry, and returns a list of ble advertizements
# discovered device

# NOTE: Python's struct.pack() will add padding bytes unless you make the endianness explicit. Little endian
# should be used for BLE. Always start a struct.pack() format string with "<"

import os
import sys
import struct
import bluetooth._bluetooth as bluez

# adding api to path
api_folder = "/home/pi/ISensitGateway/isensitgwapi/"
if api_folder not in sys.path:
    sys.path.insert(0, api_folder)
from isensit_device_adapter import *

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS = 0x00
LE_RANDOM_ADDRESS = 0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE = 7
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
OCF_LE_CREATE_CONN = 0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04

# Advertisment event types
ADV_IND = 0x00
ADV_DIRECT_IND = 0x01
ADV_SCAN_IND = 0x02
ADV_NONCONN_IND = 0x03
ADV_SCAN_RSP = 0x04


def returnnumberpacket(pkt):
    myInteger = 0
    multiple = 256
    for c in pkt:
        myInteger += struct.unpack("B", c)[0] * multiple
        multiple = 1
    return myInteger


def returnstringpacket(pkt):
    myString = ""
    for c in pkt:
        myString += "%02x" % struct.unpack("B", c)[0]
    return myString


def printpacket(pkt):
    for c in pkt:
        sys.stdout.write("%02x " % struct.unpack("B", c)[0])


def get_packed_bdaddr(bdaddr_string):
    packable_addr = []
    addr = bdaddr_string.split(':')
    addr.reverse()
    for b in addr:
        packable_addr.append(int(b, 16))
    return struct.pack("<BBBBBB", *packable_addr)


def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x' % i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))


def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)


def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)


def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def hci_le_set_scan_parameters(sock):
    try:
        old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    except Exception as e:
        print("BLE set error: ", str(e))
    else:
        SCAN_RANDOM = 0x01
        OWN_TYPE = SCAN_RANDOM
        SCAN_TYPE = 0x01

def hci_start_scan(dev_id):
    try:
        sock = bluez.hci_open_dev(dev_id)
        print("ble thread started")
    except:
        print("error accessing bluetooth device...")
        sys.exit(-1)
    else:
        hci_le_set_scan_parameters(sock)
        hci_enable_le_scan(sock)
        return sock


def parse_events(sock, loop_count=30):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
#    result = {}
  #  sock.setblocking(0)
    sock.settimeout(1.0)

    try:
        pkt = sock.recv(255)
    except Exception as e:
        print("Error in socket receiving, reason: ", str(e))
        return False 
    else:    
	if not pkt:
            print "no data received by sock"
	    return False
        else:
            ptype, event, plen = struct.unpack("BBB", pkt[:3])

            if event == LE_META_EVENT:
                subevent, = struct.unpack("B", pkt[3])
                pkt = pkt[4:]
                if subevent == EVT_LE_ADVERTISING_REPORT:
                    num_reports = struct.unpack("B", pkt[0])[0]
                    report_pkt_offset = 0
                    for i in range(0, num_reports):
#	                print pkt
       	                device_type = findDeviceType("BLESCAN", pkt)
       	                if (device_type != None):
                            jsonDict = parseDeviceStruct(deviceStruct(device_type), pkt)
		
		            return jsonDict
		        else:
		            print "Wrong Device Type"
		            return False
	        else:
		    print "Not advertising data"
		    return False
	    else:
	        print "Not LE Meta Event"
	        return False
