from typing import Optional


class SchemaStopIterationError(Exception):
    """Raised when the schema has reached the recursion limit."""


class RecursionMgr:
    def __init__(self, recursion_limit: Optional[int] = None):
        self._recursion_limit = recursion_limit
        self._manage_recursion = recursion_limit is not None

    def push(self):
        if self._manage_recursion:
            if self._recursion_limit:
                self._recursion_limit -= 1
            else:
                raise SchemaStopIterationError

    def pop(self):
        if self._manage_recursion:
            self._recursion_limit += 1
