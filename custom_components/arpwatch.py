import socket
import struct
import binascii
import time
#import json
import urllib2
from requests import post

url = 'http://garcia.h0stname.net:8123/api/services/homeassistant/turn_on'
headers = {'x-ha-access': '[ REDACTED ]','content-type': 'application/json'}

# list of Dash button mac addresses
macs = {
    '0c47c9775827' : 'scene.going_to_bed',  	### GLAD
#    '74c246183572' : 'light.right_living_room_lamp',	### ZIPLOCK
#    '0c47c9133a57' : 'light.right_bedroom_lamp'   		### PUFFS
}

# Trigger a Requests POST to HA
def trigger_url(ent_id):
	json= {'entity_id': ent_id}
	requests = post(url, headers=headers, json=json)
	print(requests.text)

rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

while True:
    packet = rawSocket.recvfrom(2048)
    ethernet_header = packet[0][0:14]
    ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)
    # skip non-ARP packets
    ethertype = ethernet_detailed[2]
    if ethertype != '\x08\x06':
        continue
    # read out data
    arp_header = packet[0][14:42]
    arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)
    source_mac = binascii.hexlify(arp_detailed[5])
    source_ip = socket.inet_ntoa(arp_detailed[6])
    dest_ip = socket.inet_ntoa(arp_detailed[8])
    if source_mac in macs:
        print ("ARP from " + source_mac + " with IP " + source_ip)
        trigger_url(macs[source_mac])
    #else:
    #	print "Unknown MAC " + source_mac + " from IP " + source_ip
