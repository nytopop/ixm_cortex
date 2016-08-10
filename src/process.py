#!/usr/bin/env python

import csv
import datetime
import math

def process_hourly(datafile, outfile, DATE_FORMAT):
    data = []
    header = []

    # NuPIC header rows
    header.append(['timestamp', 'value', 'delta', 'volume'])
    header.append(['datetime', 'float', 'float', 'float'])
    header.append(['T', '', '', ''])

    # Read input file and average/summate to 1 hour intervals
    with open(datafile, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        counter = 0
        avg = 0
        lastavg = 0
        vol_sum = 0
        seconds = 3600

        for row in csvreader:
            # set starttime to first complete hour
            if counter == 0:
                first_stamp = math.ceil(int(row[0]) / seconds) * seconds
                starttime = first_stamp

            # skip until first
            if int(row[0]) >= first_stamp:
                if int(row[0]) >= (starttime + seconds):
                    avg /= counter
                    timestamp = datetime.datetime.fromtimestamp(starttime + seconds).strftime(DATE_FORMAT)
                    data.append([timestamp, avg, (avg - lastavg), vol_sum])
                    starttime += seconds
                    counter = 0
                    lastavg = avg
                    avg = 0
                    vol_sum = 0        
                counter += 1
                avg += float(row[1])
                vol_sum += float(row[2])

    with open(outfile, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(header)
        csvwriter.writerows(data)


if __name__ == "__main__":
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    process_hourly("alg/in/btceUSD.csv", "alg/out/btceUSD.csv", DATE_FORMAT)
    process_hourly("alg/in/bitfinexUSD.csv", "alg/out/bitfinexUSD.csv", DATE_FORMAT)
    process_hourly("alg/in/bitstampUSD.csv", "alg/out/bitstampUSD.csv", DATE_FORMAT)
    process_hourly("alg/in/bitfloorUSD.csv", "alg/out/bitfloorUSD.csv", DATE_FORMAT)
    process_hourly("alg/in/coinbaseUSD.csv", "alg/out/coinbaseUSD.csv", DATE_FORMAT)
    process_hourly("alg/in/lakeUSD.csv", "alg/out/lakeUSD.csv", DATE_FORMAT)
