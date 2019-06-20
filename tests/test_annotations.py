import json
import os
import sys

# noinspection PyCompatibility
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from io import StringIO
from mypy.main import main as mypy_main
from typing import List, Dict, Any, Tuple, NewType, Optional, Union

@dataclass
class User(DataClassJsonMixin):
    id: str
    name: str = "John"


Filename = NewType('Filename', str)
LineNumber = NewType('LineNumber', int)
ErrorLevel = NewType('ErrorLevel', str)
ErrorMessage = NewType('ErrorMessage', str)

class TestAnnotations:
    u: User = User('ax9ssFxH')
    j: str = u.to_json()
    u2: User = User.from_json(j)
    u2a: User = User.from_json(j.encode())

    jMany = [{"id":"115412", "name": "Peter"}, {"id": "atxXxGhg", "name": "Parker"}]
    sch = User.schema()
    users1: List[User] = sch.loads(json.dumps(jMany), many=True)
    n: str = users1[1].name
    users2: List[User] = sch.load(jMany, many=True)
    u3: User = sch.load(jMany[1])
    j2: Dict[str, Any] = sch.dump(u)
    j3: List[Dict[str, Any]] = sch.dump([u2, u3], many=True)
    j4: str = sch.dumps(u2)

    def filter_errors(self, errors: List[str]) -> List[str]:
        real_errors: List[str] = list()
        current_file = __file__
        current_path = os.path.split(current_file)

        for line in errors:
            line = line.strip()
            if (not line):
                continue

            fn, lno, lvl, msg = self.parse_trace_line(line)
            if (fn is not None):
                _path = os.path.split(fn)
                if (_path[-1] != current_path[-1]):
                    continue

            real_errors.append(line)

        return real_errors

    def parse_trace_line(self, line: str) -> \
            Tuple[Optional[Filename], Optional[LineNumber], Optional[ErrorLevel], ErrorMessage]:
        # Define variables
        file_name: Union[str, Filename, None]
        line_no: Union[str, LineNumber, None]
        level: Union[str, ErrorLevel, None]
        msg: Union[str, ErrorMessage, None]

        where, sep, msg = line.partition(': ')
        if (sep):
            file_name, sep, line_no = where.partition(':')
            file_name = Filename(file_name)
            if (sep):
                line_no = LineNumber(int(line_no))
            else:
                line_no = None

            level, sep, msg = msg.partition(': ')
            if (sep):
                level = ErrorLevel(level)
            else:
                msg = level
                level = None

        else:
            file_name = None
            line_no = None
            level = None
            msg = line

        msg = ErrorMessage(msg)
        return file_name, line_no, level, msg


    def test_type_hints(self):
        text_io = StringIO('')
        try:
            # mypy.main uses sys.stdout for printing
            # We override it to catch error messages
            mypy_main(None, text_io, text_io, [__file__])
        except SystemExit:
            # mypy.main could return errors found inside other files.
            # filter_errors() will filter out all errors outside this file.
            errors = text_io.getvalue().splitlines()
            errors = self.filter_errors(errors)
        else:
            errors = None

        # To prevent large errors raise error out of try/except
        if (errors):
            print('\n'.join(errors))
            raise AssertionError("Type annotations check failed")
