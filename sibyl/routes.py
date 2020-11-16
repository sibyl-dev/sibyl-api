from flask import render_template
from flask_restful import Api
from flasgger import Swagger

import sibyl.resources as ctrl
from sibyl.swagger import swagger_config, swagger_tpl


API_VERSION = '/api/v1/'


def add_routes(app):

    @app.route('/redoc')
    def redoc():
        return render_template('redoc.html')

    # configure RESTful APIs
    api = Api(app)

    # configure API documentation
    Swagger(app, config=swagger_config, template=swagger_tpl, parse=True)

    # add resources
    api.add_resource(ctrl.entity.Entity,
                     API_VERSION + 'entities/<string:eid>/')
    api.add_resource(ctrl.entity.Entities, API_VERSION + 'entities/')
    api.add_resource(ctrl.entity.Events, API_VERSION + 'events/')

    api.add_resource(ctrl.referral.Referrals, API_VERSION + 'referrals/', API_VERSION + 'cases/')
    api.add_resource(ctrl.referral.Referral,
                     API_VERSION + 'referrals/<string:referral_id>/')
    # api.add_resource(ctrl.entity.EntitiesInReferral,
    #                  API_VERSION + 'entities_in_referral/<string:referral_id>/')

    api.add_resource(ctrl.feature.Feature,
                     API_VERSION + 'features/<string:feature_name>/')
    api.add_resource(ctrl.feature.Features, API_VERSION + 'features/')
    api.add_resource(ctrl.feature.Categories, API_VERSION + 'categories/')

    api.add_resource(ctrl.model.Model,
                     API_VERSION + 'models/<string:model_id>/')
    api.add_resource(ctrl.model.Models, API_VERSION + 'models/')
    api.add_resource(ctrl.model.Importance, API_VERSION + 'importance/')
    api.add_resource(ctrl.model.Prediction, API_VERSION + 'prediction/')

    api.add_resource(ctrl.computing.FeatureContributions,
                     API_VERSION + 'contributions/')
    api.add_resource(ctrl.computing.FeatureDistributions,
                     API_VERSION + 'feature_distributions/')
    api.add_resource(ctrl.computing.PredictionCount,
                     API_VERSION + 'prediction_count/')
    api.add_resource(ctrl.computing.OutcomeCount,
                     API_VERSION + 'outcome_count/')
    api.add_resource(ctrl.computing.SingleChangePredictions,
                     API_VERSION + 'single_change_predictions/')
    api.add_resource(ctrl.computing.ModifiedPrediction,
                     API_VERSION + 'modified_prediction/')

    api.add_resource(ctrl.logging.Logging, API_VERSION + 'logging/')

    api.add_resource(ctrl.test.Test, API_VERSION + 'test/')
