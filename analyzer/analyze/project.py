"""Contains Project to represent an entire UiPath project being analysed."""

import glob
import json.decoder
import os.path
from dataclasses import dataclass
from typing import Any, Iterable
import logging

from analyzer.analyze.workflow import Workflow

@dataclass
class Project():
    """Represent an entire UiPath project being analysed."""
    @staticmethod
    def get_project_properties(target_dir: str) -> dict[str, Any]:
        """Read the project.json file."""
        project_file = os.path.join(target_dir, 'project.json')
        if os.path.exists(project_file):
            return json.load(open(project_file))

        raise FileNotFoundError('No project.json found - not a valid project folder.')

    def get_workflow_files(self) -> Iterable[str]:
        """List the .xaml files (assuming all of them are workflows)."""
        return (file_name
            for file_name
            in
                glob.glob(
                    os.path.join(
                        self.project_directory,
                        './**/*.xaml'),
                    recursive=True))

    def __init__(self, project_directory):
        logging.basicConfig(level=logging.INFO)
        self.project_directory = project_directory
        properties = self.get_project_properties(project_directory)

        #  these fields can be missing in case of a template, like ReFramework.
        self.name = properties['name'] if 'name' in properties else "MISSING NAME"
        self.version = properties['projectVersion'] if 'projectVersion' in properties else "MISSING VERSION"
        self.description = properties['description']

        if 'projectType' in properties:
            self.type = properties['projectType']
        else:
            self.type = 'Workflow'

        # Libraries have no Main
        if self.type == 'Workflow':
            self.main = properties['main']

        # This assumes that each .xaml file can be processed as a workflow
        self.workflow_files = (Workflow(file_path) for file_path in self.get_workflow_files())
