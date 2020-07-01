from flask_restful import Api

import sibylapp.resources as ctrl

API_VERSION = '/api/v1/'


def add_routes(app):

    # configure RESTful APIs
    api = Api(app)

    api.add_resource(ctrl.test.Test, API_VERSION + 'test/<string:param1>/')

    api.add_resource(ctrl.entity.Entity, API_VERSION + 'entities/<string:entity_id>/')
    api.add_resource(ctrl.entity.Entities, API_VERSION + 'entities/')
