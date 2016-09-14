#!/usr/bin/python

import json
import csv
from datetime import datetime, date
import pytz
import time
import os
import calendar
import argparse
import sys
import socket

"""
Silly and simple script to import the values of a csv file into influxdb over UDP using Influxdb's line protocol
"""

def _sendLineOnUDP(msg, sock):
    """
    Send a line to influxdb through udp
    """
    msg.decode('utf-8')
    sock.sendto(msg, (UDP_IP, UDP_PORT))
    #print msg
    

def _dt2ts(dt):
    """Converts a datetime object to UTC timestamp
    naive datetime will be considered UTC.
    """

    return calendar.timegm(dt.utctimetuple())

def _try_parsing_date(text):
    for fmt in ('%d.%m.%Y %H:%M:%S','%d.%m.%Y %H:%M'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            #print 'Nothing found for format: ' + fmt
            pass
    raise ValueError('no valid date format found for '+ text)

parser = argparse.ArgumentParser(
    description='Import a CSV-file through UDP Lineprotocol into influxdb')

parser.add_argument('filename', metavar='CSV-File.csv', type=str,
                    help='The CSV-File to load data from')
parser.add_argument('-u', "--udpport", metavar='UPD-Port', default='4444',
                    type=int, dest='UDP_PORT', help='Use udp port')
parser.add_argument('-o', '--ommitLine', dest='ommitLine', action='store_true')
parser.add_argument('-t', '--timestampKey', metavar='TIMSTAMPKEY', dest='TimestampKey',
                    help="Use %(metavar)s to identify timstamp key. Default='%(default)s'", default='timestamp')

args = parser.parse_args()

UDP_IP = "127.0.0.1"  #localhost
UDP_PORT = args.UDP_PORT
Measurment = "default_measurment"
Filename = args.filename
TimestampKey = args.TimestampKey
OmmitLine2 = args.ommitLine
IgnoreValues = ["-", "NAN"]


#Set local timezone
local = pytz.timezone("Europe/Zurich")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Determine Masurment name from filename
MeasurmentName = os.path.basename(Filename)
MeasurmentName = '.'.join(MeasurmentName.split('.')[:-1]) if '.' in MeasurmentName else MeasurmentName

with open(Filename, 'rb') as csvfile:
    csv_file = csv.DictReader(csvfile, delimiter=';')
    for row in csv_file:
        firstField = True

        if OmmitLine2:
            OmmitLine2=False
            print 'Ommit Line'
            continue
              
        # create timestamp
        local_dt = local.localize(_try_parsing_date(row[TimestampKey]), is_dst=True)
        # print("LocalDT ="+local_dt.__str__())
        utc_dt = local_dt.astimezone(pytz.utc)
        # print ("UTC DT TS ="  + str(dt2ts(utc_dt)))
        timestamp = str(int(_dt2ts(utc_dt) * 1e+9))
        # Compose Line
        msg = MeasurmentName

        for key in row.keys():
            if key == TimestampKey:
                continue # ignore timestamp-row
            if row[key] in IgnoreValues or not row[key]:
                #raise ValueError("Non valid value on line #"
                # + str(csv_file.line_num))
                continue
            if firstField:
                msg += " "
                firstField = False
            else:
                msg += ","

            try:
                msg += key + "="
                msg += row[key]
            except:
                print "Unexpected error:", sys.exc_info()[0]
                print "On line: #" + str(csv_file.line_num)
                
        # append timestamp
        msg += " " + timestamp
        msg += '\n'
        print msg
        _sendLineOnUDP(msg, sock)
