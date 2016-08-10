#!/usr/bin/env python

# ixm-cortex.py

# ixm
from modelcontroller import ModelController
from data import write_db, get_csv_data, get_api_data

# nonstandard
import pymongo

# Standard libs
from multiprocessing import Pipe
from datetime import datetime
import csv
import time
import select


def main():
    # connect to mongodb, use ixm
    client = pymongo.MongoClient("mongodb://172.18.2.21")
    db = client['ixm']

    # spawn processes and feed data
    markets = ['btceUSD', 'bitfinexUSD', 'bitstampUSD', 'coinbaseUSD', 'bitfloorUSD', 'lakeUSD']
    format_string = '%Y-%m-%d %H:%M:%S'

    controllers = {}
    parents = {}
    children = {}

    for name in markets:
        # Create pipes and spawn processes
        parents[name], children[name] = Pipe()
        controllers[name] = ModelController(name, children[name])
        controllers[name].daemon = True
        controllers[name].start()

        # Ensure timestamp is indexed
        db[name].create_index([('timestamp', pymongo.ASCENDING)])
        db[name].create_index([('timestamp', pymongo.DESCENDING)])

        # get archived data from csv file
        datafile = 'alg/out/' + name + '.csv'
        data = get_csv_data(datafile)

        # get latest data from api
        latest = data[-1]['timestamp']
        latest = latest.strftime('%s')
        latest_data = get_api_data(latest, name)
        
        # add to data
        for datapoint in latest_data:
            data.append(datapoint)

        # feed data into processes
        counter = 0
        for datapoint in data:
            parents[name].send(datapoint)
            counter += 1

        print 'Fed %s datapoints into %s' % (counter, name)

    # event handling
    rlist = []
    wlist = []
    xlist = []

    # populate rlist
    for name in markets:
        rlist.append(parents[name])

    # main event loop
    counter = 0
    while True:
        ready = select.select(rlist, wlist, xlist)
        for pipe in ready[0]:
            result = pipe.recv()
            write_db(db, result)
            counter += 1
            if counter % 100 == 0:
                print 'Processed %s datapoints' % counter

    # join processes, in case while above breaks
    for name in markets:
        controllers[name].join()


if __name__=='__main__':
    main()
