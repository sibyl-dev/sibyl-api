from flask_restful import Api

import sibylapp.resources as ctrl

current_api_version = '/api/v1/'


def add_routes(app):

    # configure RESTful APIs
    api = Api(app)

    api.add_resource(ctrl.entity.Entity, current_api_version + 'entities/<string:entity_id>/')
    api.add_resource(ctrl.entity.Entities, current_api_version + 'entities/')
