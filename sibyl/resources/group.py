import logging

from flask_restful import Resource

from sibyl.db import schema

LOGGER = logging.getLogger(__name__)


def get_group(group_doc):
    group = {"group_id": group_doc.group_id, "property": group_doc.property}
    return group


class EntityGroup(Resource):
    def get(self, group_id):
        """
        Get an EntityGroup by ID
        ---
        tags:
          - group
        parameters:
          - name: group_id
            in: path
            schema:
              type: string
            required: true
            description: ID of the group to get
        responses:
          200:
            description: Group to be returned
            content:
              application/json:
                schema:
                  type: object
                  properties:
                      group_id:
                        type: string
                      property:
                        type: object
          400:
            $ref: '#/components/responses/ErrorMessage'
        """

        group = schema.EntityGroup.find_one(group_id=group_id)
        if group is None:
            LOGGER.exception("Error getting group. group %s does not exist.", group_id)
            return {"message": "group {} does not exist".format(group_id)}, 400

        return get_group(group), 200


class EntityGroups(Resource):
    def get(self):
        """
        Get all EntityGroups
        ---
        tags:
          - group
        responses:
          200:
            description: All EntityGroups
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    groups:
                      type: array
                      items:
                        type: object
                        properties:
                          group_id:
                            type: string
                          property:
                            type: object
          400:
            $ref: '#/components/responses/ErrorMessage'
        """
        documents = schema.EntityGroup.find()
        try:
            group = [document.group_id for document in documents]
        except Exception as e:
            LOGGER.exception(e)
            return {"message": str(e)}, 500
        else:
            return {"groups": group}, 200
