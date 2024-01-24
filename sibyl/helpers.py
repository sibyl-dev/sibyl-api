import logging
import pickle

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def load_realapp(model_id, include_dataset=False):
    """
    Load a realapp from a model doc
    Args:
        model_id (string): ID of model to get realapp from
        include_dataset (bool): If true, return the realapp training dataset as well

    Returns:
        success (bool): True if realapp was loaded successfully
        payload (object): If success is True, payload is (realapp, [dataset])
                          Else, payload is (error message, error code)
    """
    model_doc = schema.Model.find_one(model_id=model_id)
    if model_doc is None:
        LOGGER.exception("Error getting model. Model %s does not exist.", model_id)
        return False, ({"message": "Model {} does not exist".format(model_id)}, 400)

    realapp_bytes = model_doc.realapp
    if realapp_bytes is None:
        LOGGER.exception("Model {} does not have trained RealApp".format(model_id))
        return False, (
            {"message": "Model {} does not have trained RealApp".format(model_id)},
            400,
        )
    try:
        realapp = pickle.loads(realapp_bytes)
    except Exception as e:
        LOGGER.exception(e)
        return False, ({"message": str(e)}, 500)
    payload = (realapp,)

    if include_dataset:
        dataset_doc = model_doc.training_set
        if dataset_doc is None:
            LOGGER.exception("Error getting dataset. Model %s does not have a dataset.", model_id)
            return False, [
                {"message": "Model {} does have a dataset".format(model_id)},
                400,
            ]
        dataset = dataset_doc.to_dataframe()
        payload += (dataset,)

    return True, payload
