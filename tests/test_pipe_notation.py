def test_pipe():
    from dataclasses import dataclass
    from dataclasses_json import DataClassJsonMixin

    @dataclass(frozen=True)
    class Project(DataClassJsonMixin):
        project_id: str
        project_name: None | str = None

    p = Project(project_id='1', project_name=None)

    Project.schema().load([{"project_id": "2"}], many=True)
