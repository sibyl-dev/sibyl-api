schemas = {
    "Referral": {
        "type": "object",
        "properties": {
            "referral_id": {"type": "string"},
            "property": {"type": "object", "additionalProperties": {}},  # any
        },
        "required": ["event_id"],
    },
    "Event": {
        "type": "object",
        "properties": {
            "event_id": {"type": "string"},
            "datetime": {"type": "string"},
            "type": {"type": "string"},
            "property": {"type": "object", "additionalProperties": {}},  # any
        },
        "required": ["event_id", "message"],
    },
    "Entity": {
        "type": "object",
        "properties": {
            "eid": {"type": "string", "description": "Entity ID"},
            "row_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Row IDs",
            },
            "features": {"type": "object", "description": "Feature values"},
            "labels": {
                "type": "object",
                "description": "Ground-truth labels. Only included if available",
            },
            "property": {
                "type": "object",
                "additionalProperties": {},
                "description": "Additional properties",
            },
        },
        "required": ["eid"],
    },
    "EntityWithoutEid": {
        "type": "object",
        "properties": {
            "row_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Row IDs",
            },
            "features": {"type": "object", "description": "Feature values"},
            "labels": {
                "type": "object",
                "description": "Ground-truth labels. Only included if available",
            },
            "property": {
                "type": "object",
                "additionalProperties": {},
                "description": "Additional properties",
            },
        },
        "required": ["eid"],
    },
    "EntitySimplified": {
        "type": "object",
        "properties": {
            "eid": {"type": "string", "readOnly": True, "description": "Entity ID"},
            "row_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Row IDs",
            },
            "labels": {
                "type": "object",
                "description": "Ground-truth labels. Only included if available",
            },
            "property": {
                "type": "object",
                "additionalProperties": {},
                "description": "Additional properties",
            },
        },
        "required": ["eid"],
    },
    "Model": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Model ID"},
            "description": {"type": "string", "description": "Description of model"},
            "performance": {
                "type": "string",
                "description": "Text description of model performance metrics",
            },
        },
        "required": ["id"],
    },
    "FullModelNoRealapp": {
        "type": "object",
        "properties": {
            "description": {"type": "string", "description": "Description of model"},
            "performance": {
                "type": "string",
                "description": "Text description of model performance metrics",
            },
            "importances": {
                "type": "object",
                "description": "Feature importance scores {feature_name:score}",
            },
            "training_set_id": {
                "type": "string",
                "description": "ID of training set to use for this model",
            },
        },
    },
    "Feature": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Feature name"},
            "description": {"type": "string", "description": "Feature description"},
            "negated_description": {
                "type": "string",
                "description": "Negated feature description (for Boolean features)",
            },
            "category": {"type": "string", "description": "Category feature belongs to"},
            "type": {
                "type": "string",
                "description": "Feature type (numeric, boolean, or categorical)",
            },
        },
        "required": ["name", "type"],
    },
    "FeatureWithoutName": {
        "type": "object",
        "properties": {
            "description": {"type": "string", "description": "Feature description"},
            "negated_description": {
                "type": "string",
                "description": "Negated feature description",
            },
            "category": {"type": "string", "description": "Category feature belongs to"},
            "type": {
                "type": "string",
                "description": "Feature type (numeric, boolean, or categorical)",
            },
        },
        "required": [],
    },
    "Category": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Category name"},
            "color": {"type": "string", "description": "Color to use for category (HEX)"},
            "abbreviation": {"type": "string", "description": "Abbreviated category name"},
        },
        "required": ["name"],
    },
    "Context": {
        "type": "object",
        "properties": {
            "context_id": {"type": "string", "description": "Context ID"},
            "config": {
                "type": "object",
                "description": "context config in {config_name: config_value} format",
            },
        },
    },
    "Changes": {
        "type": "object",
        "additionalProperties": {"oneOf": [{"type": "string"}, {"type": "number"}]},
        "description": "Changes to features to  make (feature_name:new_value pairs)",
    },
    "FeatureContributions": {
        "type": "object",
        "properties": {
            "Feature Name": {"type": "string", "description": "Feature Name"},
            "Feature Value": {
                "oneOf": [{"type": "string"}, {"type": "number"}],
                "description": "Feature Value",
            },
            "Contribution": {"type": "number", "description": "Contribution to model prediction"},
            "Average/Mode": {
                "type": "number",
                "description": (
                    "Average (for numeric features) or Mode (for categorical/boolean features)"
                    " value of the feature"
                ),
            },
        },
    },
    "Message": {
        "type": "object",
        "properties": {
            "code": {"type": "string", "minimum": 100, "maximum": 600},
            "message": {"type": "string"},
        },
        "required": ["code", "message"],
    },
    "TestMessage": {
        "allOf": [
            {"$ref": "#/components/schemas/Message"},
            {
                "type": "object",
                "properties": {"data": {}},
            },
        ]
    },
}

tags = [
    {"name": "entity", "description": "Entities being analyzed"},
    {"name": "feature", "description": "ML model input features"},
    {"name": "model", "description": "The full ML model pipeline"},
    {"name": "context", "description": "Application-specific configurations"},
    {"name": "group", "description": "Entity groups"},
    {
        "name": "computing",
        "description": "Computed explanations and other ML augmenting information",
    },
    {"name": "logging", "description": "Logging user actions and system events"},
]


swagger_config = {
    "title": "Sibyl RestAPI Documentation",
    "uiversion": 3,
    "openapi": "3.0.2",
    "doc_dir": "./docs/",
    "headers": [],
    "specs": [{
        "endpoint": "apispec",
        "route": "/apispec.json",
        "rule_filter": lambda rule: True,  # all in
        "model_filter": lambda tag: True,  # all in
    }],
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    # "static_folder": "./docs/examples/",
}

markdown_text = """
<p align="left">
<img width=10% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/\
Logo_DAI_highres.png" alt=“DAI-Lab” />
<i>An open source project from Data to AI Lab at MIT.</i>
</p>

# What is Sibyl?
**Sibyl** is a highly configurable API for supporting the full human-ML decision making workflow.

# License

[The MIT License](https://github.com/sibyl-dev/sibyl-api/blob/master/LICENSE)
"""


swagger_tpl = {
    "info": {
        "description": markdown_text,
        "title": "Sibyl RestAPI Documentation",
        "version": "1.0.0",
    },
    "tags": tags,
    "components": {
        "schemas": schemas,
        "responses": {
            "SuccessMessage": {
                "description": "Success message",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/Message"}}
                },
            },
            "ErrorMessage": {
                "description": "Error message",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/Message"}}
                },
            },
        },
    },
    "servers": [
        {
            "url": "http://localhost:3000/",
            "description": "Internal staging server for testing",
        },
        {
            "url": "http://sibyl.lids.mit.edu:3000/",
            "description": "Main production server",
        },
    ],
}
