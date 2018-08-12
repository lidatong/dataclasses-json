import json
from collections.__init__ import ChainMap
from dataclasses import asdict, fields

from dataclasses_json.core import _Encoder, _decode_dataclass


class DataClassJsonMixin:
    def to_json(self, *, skipkeys=False, ensure_ascii=True, check_circular=True,
                allow_nan=True, indent=None, separators=None,
                default=None, sort_keys=False, **kw):
        return json.dumps(asdict(self),
                          cls=_Encoder,
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
    def from_json(cls,
                  kvs,
                  *,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None,
                  infer_missing=False):
        init_kwargs = json.loads(kvs,
                                 encoding=encoding,
                                 parse_float=parse_float,
                                 parse_int=parse_int,
                                 parse_constant=parse_constant)

        if infer_missing:
            init_kwargs = ChainMap(init_kwargs,
                                   {field.name: None for field in fields(cls)
                                    if field.name not in init_kwargs})
        return _decode_dataclass(cls, init_kwargs)

    @classmethod
    def from_json_array(cls,
                        kvss,
                        encoding=None,
                        parse_float=None,
                        parse_int=None,
                        parse_constant=None):
        init_kwargs_array = json.loads(kvss,
                                       encoding=encoding,
                                       parse_float=parse_float,
                                       parse_int=parse_int,
                                       parse_constant=parse_constant)
        return [_decode_dataclass(cls, init_kwargs)
                for init_kwargs in init_kwargs_array]
