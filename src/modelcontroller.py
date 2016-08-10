#!/usr/bin/env python

# modelcontroller.py

import os
import importlib
import threading
import time
from collections import deque
from multiprocessing import Process

from nupic.frameworks.opf.metrics import MetricSpec
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.predictionmetricsmanager import MetricsManager


# Should be process-safe
class ModelController(Process):
    def __init__(self, market, conn):
        super(ModelController, self).__init__()
        # runtime vars
        self.market = market
        self.conn = conn
        self.data_queue = deque()

        # set opf vars and instantiate model
        self.steps = [1, 3, 6, 12, 24, 48, 96]
        # TODO check if a model exists, if not create one
        params = self.get_params('alg.model_params.temporal-multistep_params')
        self.create_model(params)

    # Multiprocessing entry point
    def run(self):
        # spawn a worker thread to queue incoming data
        worker = threading.Thread(target=self.queuer)
        worker.daemon = True
        worker.start()
        
        # Compute items in queue
        # spinner spinner hey we have a spinner
        while True:
            while not self.data_queue:
                time.sleep(0.1)

            # get oldest queue item and compute
            datapoint = self.data_queue.popleft()
            result = self.iterate(datapoint)
            # send result to Pipe 
            self.conn.send(result)

        # just in case
        worker.join()

    # Data queuer thread
    def queuer(self):
        while True:
            # send all incoming data to the deque
            # should block when there are no incoming messages
            self.data_queue.append(self.conn.recv())

    # initialize metrics manager
    def init_metrics(self):
        metric_list = []

        # create a MetricSpec for each level of inference
        for i in self.steps:
            metric_list.append(
                MetricSpec(field='value',
                           metric='multiStep',
                           inferenceElement='multiStepBestPredictions',
                           params={'errorMetric': 'altMAPE',
                                   'window': 384,
                                   'steps': i
                           }
                )
            )

        # convert specs to tuple and initialize metrics manager
        metric_specs = tuple(metric_list)
        self.metrics_manager = MetricsManager(metric_specs,
                                              self.model.getFieldInfo(),
                                              self.model.getInferenceType())
 

    # for save/load, use alg/models dir always
    # load model from file
    def load_model(self, name):
        name = os.path.abspath(name)
        self.model = ModelFactory.loadFromCheckpoint(name)

    # save model to file
    def save_model(self, name):
        name = os.path.abspath(name)
        self.model.save(name)

    # create model from params
    def create_model(self, params):
        # create model
        self.model = ModelFactory.create(params)
        # set init params
        self.model.enableLearning()
        self.model.enableInference({'predictedField': 'value'})
        # init metrics
        self.init_metrics()

    # import model params from file
    def get_params(self, name):
        try:
            params = importlib.import_module(name).MODEL_PARAMS
        except ImportError:
            raise Exception("No model exists called %s, need to run swarming algorithm" % name)
        return params

    # iterate through a single datapoint
    def iterate(self, datapoint):
        # compute
        result = self.model.run(datapoint) 

        # run metrics
        metrics = self.metrics_manager.update(result)
       
        # scrape metrics and construct clean version
        result.metrics = {}
        for key in metrics:
            for i in self.steps:
                string = ':steps=' + str(i) + ':'
                if string in key:
                    result.metrics[i] = metrics[key]

        return (self.market, result)


if __name__=='__main__':
   mc = ModelController()
