import logging

from flask_restful import Resource

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def get_referral(referral_doc):
    referral = {
        'referral_id': referral_doc.referral_id,
        'property': referral_doc.property
    }
    return referral


class Referral(Resource):
    def get(self, referral_id):
        """
        Get a Referral by ID
        ---
        tags:
          - referral
        security:
          - tokenAuth: []
        parameters:
          - name: referral_id
            in: path
            schema:
              type: string
            required: true
            description: ID of the referral to get
        responses:
          200:
            description: Referral to be returned
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Referral'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/referral-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        referral = schema.Referral.find_one(referral_id=referral_id)
        if referral is None:
            LOGGER.exception('Error getting referral. referral %s does not exist.', referral_id)
            return {'message': 'referral {} does not exist'.format(referral_id)}, 400

        return get_referral(referral), 200


class Referrals(Resource):
    def get(self):
        """
        Get all Referrals
        ---
        tags:
          - referral
        security:
          - tokenAuth: []
        responses:
          200:
            description: All Referrals
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    referrals:
                      type: array
                      items:
                        $ref: '#/components/schemas/Referral'
                examples:
                  externalJson:
                    summary: external example
                    externalValue: '/examples/referrals-get-200.json'
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        documents = schema.Referral.find()
        try:
            referral = [document.referral_id for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {'message': str(e)}, 500
        else:
            return {'cases': referral}, 200
