import logging

from flask_restful import Resource
from flask import request
from explanation_toolkit import local_feature_explanation as lfe

LOGGER = logging.getLogger(__name__)


class Similarities(Resource):
    def get(self):
        """
        @api {get} /similar_entities/ Get similar entities
        @apiName GetSimilarities
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get a list of similar entities.

        @apiParam {String} entity_id ID of the entity.
        @apiParam {Number} number Number of similar entities to search for.

        @apiSuccess {String[]} entities List of entity IDs.
        """
        pass


class SingleChangePredictions(Resource):
    def post(self):
        """
        @api {post} /single_change_predictions/ Post single prediction 
        @apiName PostSinglePrediction
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get the list of updated predictions after making 
        single changes.

        @apiParam {String} entity_id ID of entity to predict on.
        @apiParam {String} model_id ID of model to use for predictions.
        @apiParam {2-Tuple[]} changes List of features to change and 
            their new values.
        @apiParam {String} changes.item1 Name of the feature to change.
        @apiParam {String} changes.item2 Changed Value of the feature.

        @apiSuccess {2-Tuple[]} changes List of features to change and 
            their new values.
        @apiSuccess {String} changes.item1 Name of the feature to change.
        @apiSuccess {String} changes.item2 New prediction of the feature.
        """
        entity_id = request.args.get('entity_id', None)
        model_id = request.args.get('model_id', None)
        changes = request.args.get('changes', None)
        pass


class ModifiedPrediction(Resource):
    def post(self):
        """
        @api {post} /modified_prediction/ Post multiple prediction 
        @apiName PostMultiplePrediction
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription  Get the modified prediction under different conditions

        @apiParam {String} entity_id ID of entity to predict on.
        @apiParam {String} model_id ID of model to use for predictions.
        @apiParam {2-Tuple[]} changes List of features to change and 
            their new values.
        @apiParam {String} changes.item1 Name of the feature to change.
        @apiParam {String} changes.item2 Changed Value of the feature.

        @apiSuccess {Number} prediction New prediction after making
            the requested changes.
        """
        entity_id = request.args.get('entity_id', None)
        model_id = request.args.get('model_id', None)
        changes = request.args.get('changes', None)

        predict = load_predict(model_id)  # load the prediction function associated with model_id
        entity_features = load_entity(entity_id) # load the entity's features

        features = []
        new_values = []
        for change in changes:
            features.append(change[0])
            new_values.append(change[1])

        new_pred = modify_and_repredict(
            predict, entity_features, features, new_values)
        return new_pred, 200


class FeatureDistributions(Resource):
    def post(self):
        """
        @api {post} /modified_prediction/ Get feature distributions 
        @apiName GetFeatureDistributions
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription Get the distributions of all features

        @apiParam {Number} prediction Prediction Prediction to look at distributions for.
        @apiParam {String} model_id ID of model to use for predictions.

        @apiSuccess {Object[]} distributions Information about the distributions of each
            feature for each feature.
        """
        prediction = request.args.get('prediction', None)
        model_id = request.args.get('model_id', None)

        dataset = load_dataset(model_id)
        predict = load_predict(model_id)
        features = load_features(model_id)

        boolean_features = features[
            features['Variable Type'] == 'Boolean'].index
        categorical_dataset = dataset[boolean_features]

        numeric_features = features[
            features['Variable Type'] == 'Numeric'].index
        numeric_dataset = dataset[numeric_features]

        distributions = {}
        rows = ge.get_rows_by_output(prediction, predict, dataset,
                                     row_labels=None)

        cat_summary = ge.summary_categorical(categorical_dataset.iloc[rows])
        num_summary = ge.summary_numeric(numeric_dataset.iloc[rows])

        for (i, name) in enumerate(boolean_features):
            distributions[name] = {"type": "categorical",
                                   "values": cat_summary[0][i].tolist(),
                                   "counts": cat_summary[1][i].tolist()}
        for (i, name) in enumerate(numeric_features):
            distributions[name] = {"type": "numeric",
                                   "metrics": num_summary[i]}

        return distributions


class FeatureContributions(Resource):
    def post(self):
        """
        @api {get} /computing/contributions/ Get feature contributions 
        @apiName GetFeatureContributions
        @apiGroup Computing
        @apiVersion 1.0.0
        @apiDescription  get the contributions of all features

        @apiParam {String} entity_id ID of the entity to compute.
        @apiParam {String} model ID of the model to compute.

        @apiSuccess {Object} contributions Feature contribution object (key-value pair).
        @apiSuccess {Number} contributions.[key] Contribution value of the feature [key].
        """
        entity_id = request.args.get('entity_id', None)
        model_id = request.args.get('model_id', None)

        entity_features = load_entity(entity_id)
        model = load_model(model_id)
        explainer = load_explainer(model_id)

        contributions = lfe.get_contributions(entity_features, explainer)
        return contributions, 200
