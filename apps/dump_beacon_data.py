#!/usr/bin/env python


import csv
import struct


BEACON_PDU_SIZE=62

class CSP(object):
    """
    Reused from:
    https://github.com/daniestevez/gr-satellites/blob/master/python/csp_header.py
    """

    def __init__(self, csp_bytes):
        if len(csp_bytes) < 4:
            raise ValueError("Malformed CSP packet (too short)")
        self.csp_bytes = csp_bytes
        csp = struct.unpack(">I", csp_bytes[0:4])[0]
        self.priority = (csp >> 30) & 0x3
        self.source = (csp >> 25) & 0x1f
        self.destination = (csp >> 20) & 0x1f
        self.dest_port = (csp >> 14) & 0x3f
        self.source_port = (csp >> 8) & 0x3f
        self.reserved = (csp >> 4) & 0xf
        self.hmac = (csp >> 3) & 1
        self.xtea = (csp >> 2) & 1
        self.rdp = (csp >> 1) & 1
        self.crc = csp & 1
        self.flags=int('{HMAC}{XTEA}{RDP}{CRC}'.format(HMAC=self.hmac, XTEA=self.xtea, RDP=self.rdp, CRC=self.crc))

    def toString(self):
        return ("""CSP header:
        Priority:\t\t{}
        Source:\t\t\t{}
        Destination:\t\t{}
        Destination port:\t{}
        Source port:\t\t{}
        Reserved field:\t\t{}
        HMAC:\t\t\t{}
        XTEA:\t\t\t{}
        RDP:\t\t\t{}
        CRC:\t\t\t{}""".format(
            self.priority, self.source, self.destination, self.dest_port,
            self.source_port, self.reserved, self.hmac, self.xtea, self.rdp,
            self.crc))

    def isBeacon(self):
        if self.priority == 3 and self.source == 5 and self.destination == 10 and self.dest_port == 31 and self.source_port==0 and self.getLength() == 58:
            return True
        else:
            return False

    def getCRC32C(self):
        calculated_CRC32C = Crc32c.calc(self.csp_bytes)
        return calculated_CRC32C

    def getLength(self):
        return len(self.csp_bytes)

    def getHex(self):
        return self.csp_bytes.hex()

    def getBeaconContents(self):
        if self.isBeacon():
            payload = struct.unpack('>4h 4I B H 2I h B 4I', self.csp_bytes[4:]) #nanocom beacon format
            return payload



f = open('csp_frames.bin', 'rb')
fout = open ('beacons.csv', 'w')
beacons = []
processed = 0
while True:
    pdu = f.read(BEACON_PDU_SIZE)
    if not pdu:
        break
    csp = CSP(pdu[:(len(pdu)-4)])
    processed += 1
    #print("Processing CSP {}".format(csp.toString()))
    if csp.isBeacon():
        temp_brd,\
        temp_pa,\
        last_rssi,\
        last_rferr,\
        tx_count,\
        rx_count,\
        tx_bytes,\
        rx_bytes,\
        active_conf,\
        boot_count,\
        boot_cause,\
        last_contact,\
        bgnd_rssi,\
        tx_duty,\
        tot_tx_count,\
        tot_rx_count,\
        tot_tx_bytes,\
        tot_rx_bytes =  csp.getBeaconContents()
        beacon = {"temp_brd": temp_brd,
            "temp_pa": temp_pa,
            "last_rssi": last_rssi,
            "last_rferr": last_rferr,
            "tx_count": tx_count,
            "rx_count": rx_count,
            "tx_bytes": tx_bytes,
            "rx_bytes": rx_bytes,
            "active_conf": active_conf,
            "boot_count": boot_count,
            "boot_cause": boot_cause,
            "last_contact": last_contact,
            "bgnd_rssi": bgnd_rssi,
            "tx_duty": tx_duty,
            "tot_tx_count": tot_tx_count,
            "tot_rx_count": tot_rx_count,
            "tot_tx_bytes": tot_tx_bytes,
            "tot_rx_bytes": tot_rx_bytes,}
        beacons.append(beacon)

#print(beacons)

if len(beacons) > 0:
    writer = csv.DictWriter(fout, fieldnames=beacons[0].keys())
    writer.writeheader()
    writer.writerows(beacons)
fout.close()
print('Processed PDUs {}, found {} beacons'.format(processed, len(beacons)))
print('All beacons written')
    
