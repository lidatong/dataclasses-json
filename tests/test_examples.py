from dataclasses import dataclass
from typing import Set, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class Student:
    id: int = 0
    name: str = ""


@dataclass_json
@dataclass
class Tutor:
    id: int
    student: Optional[Student]


@dataclass_json
@dataclass(frozen=True)
class Professor:
    id: int
    name: str


@dataclass_json
@dataclass(frozen=True)
class Course:
    id: int
    name: str
    professor: Professor
    students: Set[Student]


s1 = Student(1, 'student')
s2 = Student(2, 'student')
t = Tutor(id=1, student=None)
p = Professor(1, 'professor')
c = Course(1, 'course', p, {s1})


class TestEncoder:
    def test_student(self):
        assert s1.to_json() == '{"id": 1, "name": "student"}'

    def test_professor(self):
        assert p.to_json() == '{"id": 1, "name": "professor"}'

    def test_course(self):
        assert c.to_json() == '{"id": 1, "name": "course", "professor": {"id": 1, "name": "professor"}, "students": [{"id": 1, "name": "student"}]}'

    def test_students_missing(self):
        s1_anon = Student(1, '')
        s2_anon = Student(2, '')
        one = [s1_anon, s2_anon]
        two = [s2_anon, s1_anon]
        actual = Student.schema().loads('[{"id": 1}, {"id": 2}]', many=True)
        assert actual == one or actual == two


class TestDecoder:
    def test_tutor(self):
        assert Tutor.from_json('{"id": 1}', infer_missing=True) == t
