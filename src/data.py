#!/usr/bin/env python

# database.py

import csv
import requests
import math
from datetime import datetime

from pymongo import MongoClient


# write a result tuple (market, ModelResult) to the db
def write_db(db, result):
    # construct doc and filter doc
    doc = construct_doc(result[1])
    filt = {'timestamp': doc['timestamp']}

    # write doc to collection
    db[result[0]].update_one(filt, {'$set': doc}, upsert=True)


# ModelResult to doc
def construct_doc(res):
    timestamp = res.rawInput['timestamp'].strftime('%s')
    timestamp = int(timestamp)
    doc = {
        # convert datetime object to unixtime
        'timestamp': timestamp,
        'input': {
            'value': res.rawInput['value'],
            'delta': res.rawInput['delta'],
            'volume': res.rawInput['volume']
        },
        'inferences': {
            '1': res.inferences['multiStepBestPredictions'][1],
            '3': res.inferences['multiStepBestPredictions'][3],
            '6': res.inferences['multiStepBestPredictions'][6],
            '12': res.inferences['multiStepBestPredictions'][12],
            '24': res.inferences['multiStepBestPredictions'][24],
            '48': res.inferences['multiStepBestPredictions'][48],
            '96': res.inferences['multiStepBestPredictions'][96]
        },
        'metrics': {
            '1': res.metrics[1],
            '3': res.metrics[3],
            '6': res.metrics[6],
            '12': res.metrics[12],
            '24': res.metrics[24],
            '48': res.metrics[48],
            '96': res.metrics[96]
        }
    }
    return doc


# read api and return [{}]
def get_api_data(start, market):
    data = [] 
    # construct api
    url = 'http://api.bitcoincharts.com/v1/trades.csv?symbol=' + market + '&start=' + str(start)
        
    response = requests.get(url)
    
    start = int(start)
    counter = 1
    avg = 0
    lastavg = 0
    vol_sum = 0
    seconds = 3600

    for item in response.iter_lines():
        elems = item.split(',')
        
        if int(elems[0]) >= (start + seconds):
            avg /= counter
            # convert unixtime to datetime
            timestamp = datetime.fromtimestamp(start + seconds)
            data.append({'timestamp': timestamp,
                         'value': avg,
                         'delta': avg - lastavg,
                         'volume': vol_sum})
            start += seconds
            lastavg = avg
            counter = 0
            avg = 0
            vol_sum = 0
        counter += 1
        avg += float(elems[1])
        vol_sum += float(elems[2])
    return data


# read csv datafile and return [{}]
def get_csv_data(datafile):
    data = []

    # iterate through csv file
    with open(datafile, 'rb') as csvfile:
        # skip header
        csvreader = csv.reader(csvfile, delimiter=',')
        csvreader.next()
        csvreader.next()
        csvreader.next()

        counter = 0
        format_string = '%Y-%m-%d %H:%M:%S'

        # iterate
        for row in csvreader:
            # convert timestamp to datetime
            timestamp = datetime.strptime(row[0], format_string)
            datapoint = {'timestamp': timestamp,
                         'value': float(row[1]),
                         'delta': float(row[2]),
                         'volume': float(row[3])}
            data.append(datapoint)
            counter += 1
    return data


if __name__=='__main__':
    get_api_data(44444, 'btceUSD')
    get_csv_data('alg/out/btceUSD.csv')
