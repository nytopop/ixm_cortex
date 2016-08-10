#!/bin/sh

apt-get update
apt-get install python-pip python-dev

pip install https://s3-us-west-2.amazonaws.com/artifacts.numenta.org/numenta/nupic.core/releases/nupic.bindings/nupic.bindings-0.4.4-cp27-none-linux_x86_64.whl

pip install nupic
pip install pymongo
