#!/usr/bin/python

import json
import csv
from datetime import datetime, date
import pytz
import time
import os
import calendar
import argparse

import socket


def _sendLineOnUDP(msg, sock):
    """
    Send a line to influxdb through udp
    """
    msg.decode('utf-8')
    #sock.sendto(msg, (UDP_IP, UDP_PORT))
    print msg


def _dt2ts(dt):
    """Converts a datetime object to UTC timestamp
    naive datetime will be considered UTC.
    """

    return calendar.timegm(dt.utctimetuple())

UDP_PORT = 4444

parser = argparse.ArgumentParser(description='Import CSV throug UDP Lineprotocol into influxdb')

parser.add_argument('filename', metavar='CSV-File.csv', type=str,
                   help='The CSV-File to load data from')
parser.add_argument('-u', "--udp-port", metavar='UPD-Port#', default=4444,
                   action='store_const', const=UDP_PORT, type=int, 
                   help='Use udp port')

args = parser.parse_args()



UDP_IP = "127.0.0.1"  # localhost
UDP_PORT = args.u
Measurment = "default_measurment"
Filename = args.filename
TimestampKey = ""



# Set local timezone
local = pytz.timezone("Europe/Zurich")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Determine Masurment name from filename
MeasurmentName = os.path.splitext(Filename)[0]

with open(Filename, 'rb') as csvfile:
    csv_file = csv.DictReader(csvfile, delimiter=';')
    for row in csv_file:
        firstField = True
        # try to find timestamp row
        if not TimestampKey:
            if 'timestamp' in row:
                TimestampKey = 'timestamp'
            else:
                raise ValueError("Can't deterimine csv-key for timestamp")

        # create timestamp
        local_dt = local.localize(datetime.strptime(row[TimestampKey], '%d.%m.%Y %H:%M'), is_dst=True)
        #print("LocalDT ="+local_dt.__str__())
        utc_dt = local_dt.astimezone(pytz.utc)
        #print ("UTC DT TS ="  + str(dt2ts(utc_dt)))
        timestamp = str(int(_dt2ts(utc_dt) * 1e+9))
        # Compose Line
        msg = MeasurmentName

        for key in row.keys():
            if key == TimestampKey:
                continue
            if row[key] is "-" or not row[key]:
                #raise ValueError("Non valid value on line #" + str(csv_file.line_num))
                continue
            if firstField:
                msg += " "
                firstField = False
            else:
                msg += ","

            msg += key + "="
            msg += row[key]

        # append timestamp
        msg += " "+ row[TimestampKey]
        msg += '\n'
        print msg
        _sendLineOnUDP(msg, sock)
