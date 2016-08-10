SWARM_DESCRIPTION = {
  "includedFields": [
    {
      "fieldName": "timestamp",
      "fieldType": "datetime"
    },
    {
      "fieldName": "value",
      "fieldType": "float"
    },
    {
      "fieldName": "delta",
      "fieldType": "float"
    },
    {
      "fieldName": "volume",
      "fieldType": "float"
    }
  ],
  "streamDef": {
    "info": "temporal-multistep",
    "version": 1,
    "streams": [
      {
        "info": "btceUSD.csv",
        "source": "file://alg/out/btceUSD.csv",
        "columns": [
          "*"
        ]
      }
    ]
  },
  "inferenceType": "TemporalMultiStep",
  "inferenceArgs": {
    "predictionSteps": [
      1,3,6,12,24,48,96
    ],
    "predictedField": "value"
  },
  "iterationCount": -1,
  "swarmSize": "small"
}
