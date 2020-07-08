from flask_restful import Api

import sibylapp.resources as ctrl

API_VERSION = '/api/v1/'


def add_routes(app):

    # configure RESTful APIs
    api = Api(app)

    api.add_resource(ctrl.test.Test, API_VERSION + 'test/<string:param1>/')

    api.add_resource(ctrl.entity.Entity, API_VERSION + 'entities/<string:entity_id>/')
    api.add_resource(ctrl.entity.Entities, API_VERSION + 'entities/')
    api.add_resource(ctrl.entity.Outcome, API_VERSION + 'outcome/')

    api.add_resource(ctrl.feature.Feature, API_VERSION + 'features/<string:feature_name>/')
    api.add_resource(ctrl.feature.Features, API_VERSION + 'features/')
    api.add_resource(ctrl.feature.Categories, API_VERSION + 'categories/')

    api.add_resource(ctrl.model.Model, API_VERSION + 'models/<string:model_id>/')
    api.add_resource(ctrl.model.Models, API_VERSION + 'models/')
    api.add_resource(ctrl.model.Importance, API_VERSION + 'importance/')
    api.add_resource(ctrl.model.Prediction, API_VERSION + 'prediction/')

    api.add_resource(ctrl.computing.FeatureContributions, API_VERSION + 'computing/contributions/')
