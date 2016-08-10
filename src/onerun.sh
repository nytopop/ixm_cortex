#!/bin/bash

cd "alg"
cd "in"

#wget "https://api.bitcoincharts.com/v1/csv/btceUSD.csv.gz"
#wget "https://api.bitcoincharts.com/v1/csv/bitfinexUSD.csv.gz"
#wget "https://api.bitcoincharts.com/v1/csv/bitstampUSD.csv.gz"
#wget "https://api.bitcoincharts.com/v1/csv/bitfloorUSD.csv.gz"
#wget "https://api.bitcoincharts.com/v1/csv/coinbaseUSD.csv.gz"
#wget "https://api.bitcoincharts.com/v1/csv/lakeUSD.csv.gz"

#gunzip *

cd ../..

python process.py
python ixm_cortex.py
