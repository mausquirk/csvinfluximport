# cscinflux python import

Silly and simple script to import the values of a csv file into influxdb over UDP using the [line protocol](https://docs.influxdata.com/influxdb/v0.13/write_protocols/line).

## Usage

```
usage: csvinfluximport.py [-h] [-u UPD-Port#] CSV-File.csv

Import a CSV-file through UDP Lineprotocol into influxdb

positional arguments:
  CSV-File.csv          The CSV-File to load data from

optional arguments:
  -h, --help            show this help message and exit
    -u UPD-Port#, --udpport UPD-Port#
                            Use udp port

```

## Mapping of fields
###  Measurement Name 
The `CSV-File`-name without `.csv` extension will be used as measurement name.
### Fields
The top row of the CSV-file is considered to hold the key-name (column-header) for every column.
The values are built as follow `CSV-ColumnHeader = CSV`

### timestamp
The script tries to determine the value timestamp itself. It looks for the Column-header named `timestamp`;)
Currently the csv-timestamp is considered to be a in `%d.%m.%Y %H:%M`(24hours)-format and in local Central European time.
The timestamp will be converted to UTC Time for influximport.

## Future extensions / Todos
- Specify the timestamp-column as option
- Specify the local-time zone as option or skip the time conversion in case the timestamp is already UTC
- 


