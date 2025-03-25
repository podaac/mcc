"""
=============
json_utils.py
=============

Contains a custom JSON encoding function for non-primitive Python types.

"""

from collections import deque

import numpy as np
from flask.json import JSONEncoder

from checker.base import Result


class CustomJSONEncoder(JSONEncoder):
    """
    Provides conversion to JSON-encodable types of custom python classes
    and types that would otherwise throw exceptions.
    """
    def default(self, obj):
        if isinstance(obj, Result):
            return vars(obj)
        if isinstance(obj, deque):
            return [x for x in obj]
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)

        # Fallback to default encoder for all other types, and if that fails
        # just cast to string representation
        try:
            return JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)
