from dataclasses import dataclass
from typing import Set

from marshmallow import Schema, fields

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class Student:
    id: int
    name: str


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


s = Student(1, 'student')
p = Professor(1, 'professor')
c = Course(1, 'course', p, {s})


class StudentSchema(Schema):
    class Meta:
        fields = ('id', 'name')


class ProfessorSchema(Schema):
    class Meta:
        fields = ('id', 'name')


class CourseSchema(Schema):
    class Meta:
        fields = ('id', 'name', 'professor', 'students')

    professor = fields.Nested(ProfessorSchema)
    students = fields.Nested(StudentSchema, many=True)


class TestEncoder:
    def test_student(self):
        assert s.to_json() == '{"id": 1, "name": "student"}'

    def test_professor(self):
        assert p.to_json() == '{"id": 1, "name": "professor"}'

    def test_course(self):
        assert c.to_json() == '{"id": 1, "name": "course", "professor": {"id": 1, "name": "professor"}, "students": [{"id": 1, "name": "student"}]}}'
