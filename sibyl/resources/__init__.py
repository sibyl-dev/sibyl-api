"""Sybyl RestAPIs Resources.

This subpackage contains all the code related to the API Resource usage.
"""
from sibyl.resources import (computing, entity, feature,
                             logging, model, test, group, context)

__all__ = (
    'entity',
    'feature',
    'model',
    'computing',
    'test',
    'logging',
    'group.py',
    'context.py'
)
