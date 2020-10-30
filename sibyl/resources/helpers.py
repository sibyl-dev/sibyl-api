import logging
import pickle

from sibylapp.db import schema

LOGGER = logging.getLogger(__name__)


def load_model(model_id, include_dataset=False, include_explainer=False):
    """
    Load a model and its components
    :param model_id: string
           Database id of the model wanted
    :param include_dataset: boolean
           If true, return the model dataset as well
    :param include_explainer: boolean
       If true, return the trained model explainer as well
    :return: success->boolean, payload->object
             If success is True, payload is (model, transformer, [dataset], [explainer])
             Else, payload is (error message, error code)
    """
    model_doc = schema.Model.find_one(id=model_id)
    if model_doc is None:
        LOGGER.exception('Error getting model. Model %s does not exist.', model_id)
        return False, ({'message': 'Model {} does not exist'.format(model_id)}, 400)
    model_bytes = model_doc.model
    try:
        model = pickle.loads(model_bytes)
    except Exception as e:
        LOGGER.exception(e)
        return False, ({'message': str(e)}, 500)

    transformer_bytes = model_doc.transformer
    transformer = None
    if transformer_bytes is not None:
        try:
            transformer = pickle.loads(transformer_bytes)
        except Exception as e:
            LOGGER.exception(e)
            return False, ({'message': str(e)}, 500)

    payload = (model, transformer)
    if include_dataset:
        dataset_doc = model_doc.training_set
        if dataset_doc is None:
            LOGGER.exception('Error getting dataset. Model %s does not have a dataset.', model_id)
            return False, [{'message': 'Model {} does have a dataset'.format(model_id)}, 400]
        dataset = dataset_doc.to_dataframe()
        payload += (dataset, )

    if include_explainer:
        explainer_bytes = model_doc.explainer
        if explainer_bytes is None:
            LOGGER.exception('Model %s explainer has not been trained. ', model_id)
            return False, ({'message': 'Model {} does not have trained explainer'
                            .format(model_id)}, 400)
        try:
            explainer = pickle.loads(explainer_bytes)
            payload += (explainer, )
        except Exception as e:
            LOGGER.exception(e)
            return False, ({'message': str(e)}, 500)

    return True, payload
