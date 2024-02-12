import json

from flasgger import Swagger
from flask import render_template
from flask_restful import Api

import sibyl.resources as ctrl
from sibyl.swagger import swagger_config, swagger_tpl

API_VERSION = "/api/v1/"


def add_routes(app, docs_filename=None):
    @app.route("/redoc")
    def redoc():
        return render_template("redoc.html")

    # configure RESTful APIs
    api = Api(app)

    # configure API documentation
    swag = Swagger(app, config=swagger_config, template=swagger_tpl, parse=True)

    # add resources
    api.add_resource(ctrl.entity.Entity, API_VERSION + "entities/<string:eid>/")
    api.add_resource(ctrl.entity.Entities, API_VERSION + "entities/")

    api.add_resource(ctrl.group.EntityGroups, API_VERSION + "groups/")
    api.add_resource(ctrl.group.EntityGroup, API_VERSION + "groups/<string:group_id>/")

    api.add_resource(ctrl.feature.Feature, API_VERSION + "features/<string:feature_name>/")
    api.add_resource(ctrl.feature.Features, API_VERSION + "features/")
    api.add_resource(ctrl.feature.Categories, API_VERSION + "categories/")

    api.add_resource(ctrl.model.Model, API_VERSION + "models/<string:model_id>/")
    api.add_resource(ctrl.model.Models, API_VERSION + "models/")
    api.add_resource(ctrl.model.Importance, API_VERSION + "importance/")
    api.add_resource(ctrl.model.Prediction, API_VERSION + "prediction/")
    api.add_resource(ctrl.model.MultiPrediction, API_VERSION + "multi_prediction/")

    api.add_resource(ctrl.context.Context, API_VERSION + "context/<string:context_id>/")
    api.add_resource(ctrl.context.Contexts, API_VERSION + "contexts/")

    api.add_resource(ctrl.computing.FeatureContributions, API_VERSION + "contributions/")
    api.add_resource(
        ctrl.computing.MultiFeatureContributions, API_VERSION + "multi_contributions/"
    )
    api.add_resource(
        ctrl.computing.SingleChangePredictions,
        API_VERSION + "single_change_predictions/",
    )
    api.add_resource(ctrl.computing.ModifiedPrediction, API_VERSION + "modified_prediction/")
    api.add_resource(
        ctrl.computing.ModifiedFeatureContribution, API_VERSION + "modified_contribution/"
    )
    api.add_resource(ctrl.computing.SimilarEntities, API_VERSION + "similar_entities/")

    api.add_resource(ctrl.logger.Logger, API_VERSION + "logging/")

    if docs_filename:
        with open(docs_filename, "w") as fp:
            with app.app_context():
                json.dump(swag.get_apispecs(endpoint=swagger_config["specs"][0]["endpoint"]), fp)
