define({ "api": [
  {
    "type": "post",
    "url": "/contributions/",
    "title": "Get feature contributions",
    "name": "GetFeatureContributions",
    "group": "Computing",
    "version": "1.0.0",
    "description": "<p>get the contributions of all features</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "eid",
            "description": "<p>ID of the entity to compute.</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "model_id",
            "description": "<p>ID of the model to compute.</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "contributions",
            "description": "<p>Feature contribution object (key-value pair).</p>"
          },
          {
            "group": "Success 200",
            "type": "Number",
            "optional": false,
            "field": "contributions.[key]",
            "description": "<p>Contribution value of the feature [key].</p>"
          }
        ]
      }
    },
    "filename": "sibyl/resources/computing.py",
    "groupTitle": "Computing"
  },
  {
    "type": "post",
    "url": "/feature_distributions/",
    "title": "Get feature distributions",
    "name": "PostFeatureDistributions",
    "group": "Computing",
    "version": "1.0.0",
    "description": "<p>Get the distributions of all features</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "prediction",
            "description": "<p>Prediction Prediction to look at distributions for.</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "model_id",
            "description": "<p>ID of model to use for predictions.</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "distributions",
            "description": "<p>Information about the distributions of each feature for each feature.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "distributions.key",
            "description": "<p>Feature name</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "allowedValues": [
              "\"numeric\"",
              "\"categorical\""
            ],
            "optional": false,
            "field": "distributions.type",
            "description": "<p>Feature type</p>"
          },
          {
            "group": "Success 200",
            "type": "5-tuple",
            "optional": false,
            "field": "distributions.metrics",
            "description": "<p>If type is &quot;numeric&quot;:[min, 1st quartile, median, 3rd quartile, max] <br>. If type is &quot;categorical&quot;: [[values],[counts]]</p>"
          }
        ]
      }
    },
    "filename": "sibyl/resources/computing.py",
    "groupTitle": "Computing"
  },
  {
    "type": "post",
    "url": "/modified_prediction/",
    "title": "Post multiple prediction",
    "name": "PostMultiplePrediction",
    "group": "Computing",
    "version": "1.0.0",
    "description": "<p>Get the modified prediction under different conditions</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "eid",
            "description": "<p>ID of entity to predict on.</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "model_id",
            "description": "<p>ID of model to use for predictions.</p>"
          },
          {
            "group": "Parameter",
            "type": "2-Tuple[]",
            "optional": false,
            "field": "changes",
            "description": "<p>List of features to change and their new values.</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "changes.item1",
            "description": "<p>Name of the feature to change.</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "changes.item2",
            "description": "<p>Changed Value of the feature.</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Number",
            "optional": false,
            "field": "prediction",
            "description": "<p>New prediction after making the requested changes.</p>"
          }
        ]
      }
    },
    "filename": "sibyl/resources/computing.py",
    "groupTitle": "Computing"
  },
  {
    "type": "post",
    "url": "/outcome_count/",
    "title": "Get outcome count",
    "name": "PostOutcomeCount",
    "group": "Computing",
    "version": "1.0.0",
    "description": "<p>Get the distributions of entity outcomes that were predicted as a certain value</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "prediction",
            "description": "<p>Prediction Prediction to look at counts for</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "model_id",
            "description": "<p>ID of model to use for predictions.</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "distributions",
            "description": "<p>Information about the distributions of each outcome.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "distributions.key",
            "description": "<p>Outcome name</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "allowedValues": [
              "\"numeric\"",
              "\"category\""
            ],
            "optional": false,
            "field": "distributions.type",
            "description": "<p>Outcome type</p>"
          },
          {
            "group": "Success 200",
            "type": "5-tuple",
            "optional": false,
            "field": "distributions.metrics",
            "description": "<p>If type is &quot;numeric&quot;: [min, 1st quartile, median, 3rd quartile, max] <br> If type is &quot;categorical&quot; or &quot;binary&quot;: [[values],[counts]]</p>"
          }
        ]
      }
    },
    "filename": "sibyl/resources/computing.py",
    "groupTitle": "Computing"
  },
  {
    "type": "post",
    "url": "/prediction_count/",
    "title": "Get prediction count",
    "name": "PostPredictionCount",
    "group": "Computing",
    "version": "1.0.0",
    "description": "<p>Get the number of entities that were predicted as a certain value</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "prediction",
            "description": "<p>Prediction to look at counts for</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "model_id",
            "description": "<p>ID of model to use for predictions.</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Number",
            "optional": false,
            "field": "count",
            "description": "<p>Number of entities who are predicted as prediction in the training set</p>"
          }
        ]
      }
    },
    "filename": "sibyl/resources/computing.py",
    "groupTitle": "Computing"
  },
  {
    "type": "post",
    "url": "/logging/",
    "title": "Save a log message",
    "name": "PostLogging",
    "group": "Logging",
    "version": "1.0.0",
    "description": "<p>Save information to the log.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "event",
            "description": "<p>Details of event to log</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "event.element",
            "description": "<p>Element that was interacted with</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "allowedValues": [
              "\"click\"",
              "\"type\"",
              "\"filter\""
            ],
            "optional": false,
            "field": "event.action",
            "description": "<p>click=clicked on button, type=filled in textbox, filter=filtered a table)</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "event.details",
            "description": "<p>Details of event (text that was put in textbox, filter that was selected)</p>"
          },
          {
            "group": "Parameter",
            "type": "Float",
            "optional": false,
            "field": "timestamp",
            "description": "<p>Timestamp of the event in seconds since Epoch</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "user_id",
            "description": "<p>Id of user using the app</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "eid",
            "description": "<p>Id of entity involved</p>"
          }
        ]
      }
    },
    "filename": "sibyl/resources/logging.py",
    "groupTitle": "Logging"
  }
] });
