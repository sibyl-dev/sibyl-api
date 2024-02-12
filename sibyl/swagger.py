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
            "id": {"type": "string"},
            "description": {"type": "string"},
            "performance": {"type": "string"},
        },
        "required": ["id"],
    },
    "FullModelNoRealapp": {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "performance": {"type": "string"},
            "importances": {"type": "object"},
            "training_set_id": {"type": "string"},
        },
    },
    "Feature": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "negated_description": {"type": "string"},
            "category": {"type": "string"},
            "type": {"type": "string"},
        },
        "required": ["name", "type"],
    },
    "FeatureWithoutName": {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "negated_description": {"type": "string"},
            "category": {"type": "string"},
            "type": {"type": "string"},
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
        "properties": {"config": {"type": "object"}},
    },
    "Changes": {
        "type": "object",
        "additionalProperties": {"oneOf": [{"type": "string"}, {"type": "number"}]},
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
