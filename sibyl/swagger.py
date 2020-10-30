schemas = {
    'Referral': {
        'type': 'object',
        'properties': {
            'referral_id': {'type': 'string'},
            'property': {'type': 'object', 'additionalProperties': {}}  # any
        },
        'required': ['event_id']
    },
    'Event': {
        'type': 'object',
        'properties': {
            'event_id': {'type': 'string'},
            'datetime': {'type': 'string'},
            'type': {'type': 'string'},
            'property': {'type': 'object', 'additionalProperties': {}}  # any
        },
        'required': ['event_id', 'message']
    },
    'Entity': {
        'type': 'object',
        'properties': {
            'eid': {'type': 'string'},
            'features': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'value': {
                            'oneOf': [
                                {'type': 'string'},
                                {'type': 'integer'},
                                {'type': 'number'}
                            ]
                        },
                    }
                },

            },
            'property': {'type': 'object', 'additionalProperties': {}}  # any
        },
        'required': ['code', 'message']
    },
    'Message': {
        'type': 'object',
        'properties': {
            'code': {'type': 'string', 'minimum': 100, 'maximum': 600},
            'message': {'type': 'string'}
        },
        'required': ['code', 'message']
    },
    'TestMessage': {
        'allOf': [
            {'$ref': '#/components/schemas/Message'},
            {
                'type': 'object',
                'properties': {
                    'data': {}
                },
            }
        ]
    }
}

tags = [
    {
        'name': 'default',
        'description': 'Uncategorized APIs'
    },
    {
        'name': 'entity',
        'description': 'Everything about entity interactions'
    },
    {
        'name': 'referral',
        'description': 'Everything about referral interactions'
    },
]


swagger_config = {
    'title': 'Sibyl RestAPI Documentation',
    'uiversion': 3,
    'openapi': '3.0.2',
    'doc_dir': './apidocs/resources/',
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    'swagger_ui': True,
    'specs_route': '/apidocs/',
    # 'static_folder': './apidocs/examples/'
}

markdown_text = """
<p align="left">
<img width=10% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/\
Logo_DAI_highres.png" alt=“DAI-Lab” />
<i>An open source project from Data to AI Lab at MIT.</i>
</p>

# What is Sibyl?
**Sibyl** introduction goes here!

# License

[The MIT License](https://github.com/DAI-Lab/sibyl-api/blob/master/LICENSE)
"""


swagger_tpl = {
    'info': {
        'description': markdown_text,
        'title': 'Sibyl RestAPI Documentation',
        'version': '1.0.0'
    },
    'tags': tags,
    'components': {
        'schemas': schemas,
        'responses': {
            'SuccessMessage': {
                'description': 'Success message',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Message'}
                    }
                }
            },
            'ErrorMessage': {
                'description': 'Error message',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Message'}
                    }
                }
            }
        }
    },
    'servers': [
        {
            'url': 'http://localhost:3000/',
            'description': 'Internal staging server for testing'
        },
        {
            'url': 'http://sibyl.lids.mit.edu:3000/',
            'description': 'Main production server'
        }
    ]
}
