"""Test loading an entire project, and reading some of its metadata."""

from os.path import join, dirname

from analyzer.analyze.project import Project

def test_project():
    """Test values read from project.json"""
    project_directory: str = join(dirname(__file__), 'assets/')
    project: Project = Project(project_directory)

    assert project.name == "MISSING NAME"
    assert project.description == "UiPath REFramework Template"
