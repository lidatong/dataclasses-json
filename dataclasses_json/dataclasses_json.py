import json

from dataclasses import asdict, fields, is_dataclass
from typing import Set, Tuple


class DataClassEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Set):
            return list(o)
        return json.JSONEncoder.default(self, o)


class DataClassJsonMixin:
    _supported_types = {Set, Tuple}

    def to_dict(self):
        return asdict(self)

    def to_json(self, skipkeys=False, ensure_ascii=True, check_circular=True,
                allow_nan=True, indent=None, separators=None,
                default=None, sort_keys=False, **kw):
        return json.dumps(self.to_dict(),
                          cls=DataClassEncoder,
                          skipkeys=skipkeys,
                          ensure_ascii=ensure_ascii,
                          check_circular=check_circular,
                          allow_nan=allow_nan,
                          indent=indent,
                          separators=separators,
                          default=default,
                          sort_keys=sort_keys,
                          **kw)

    @classmethod
    def from_dict(cls, kvs):
        init_kwargs = {}
        for field in fields(cls):
            if is_dataclass(field.type):
                init_kwargs[field.name] = field.type.from_dict(kvs[field.name])
            elif issubclass(field.type, Tuple):
                init_kwargs[field.name] = tuple(kvs[field.name])
            elif issubclass(field.type, Set):
                init_kwargs[field.name] = set(kvs[field.name])
            else:
                init_kwargs[field.name] = kvs[field.name]
        return cls(**init_kwargs)

    @classmethod
    def from_json(cls,
                  kvs,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None):
        init_kwargs = json.loads(kvs,
                                 encoding=encoding,
                                 parse_float=parse_float,
                                 parse_int=parse_int,
                                 parse_constant=parse_constant)
        return cls.from_dict(init_kwargs)
