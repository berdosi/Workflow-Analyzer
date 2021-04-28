"""Contains Project to represent an entire UiPath project being analysed."""

from glob import glob
import json.decoder
from os.path import join, dirname, exists
from dataclasses import dataclass
from typing import Any, Iterable, Dict
import logging

from analyzer.analyze.workflow import Workflow

# As the analyzer can be checked out within the to-be-analyzed project,
# its own test files are to be excluded from the direcetory listing.
TEST_ASSET_DIR = '/tests/assets'

@dataclass
class Project():
    """Represent an entire UiPath project being analysed."""

    @staticmethod
    def get_project_properties(target_dir: str) -> Dict[str, Any]:
        """Read the project.json file."""
        project_file = join(target_dir, 'project.json')
        if exists(project_file):
            return json.load(open(project_file))

        raise FileNotFoundError('No project.json found - not a valid project folder.')

    def get_workflow_files(self) -> Iterable[str]:
        """List the .xaml files (assuming all of them are workflows)."""
        return (file_name
            for file_name
            in
                glob(
                    join(
                        self.project_directory,
                        './**/*.xaml'),
                    recursive=True)
                if not dirname(file_name).endswith(TEST_ASSET_DIR))

    def __init__(self, project_directory):
        logging.basicConfig(level=logging.INFO)
        self.project_directory = project_directory
        properties = self.get_project_properties(project_directory)

        #  these fields can be missing in case of a template, like ReFramework.
        self.name = properties['name'] if 'name' in properties else "MISSING NAME"
        self.version = (properties['projectVersion']
            if 'projectVersion' in properties
            else "MISSING VERSION")
        self.description = properties['description']

        if 'projectType' in properties:
            self.type = properties['projectType']
        else:
            self.type = 'Workflow'

        # Libraries have no Main
        if self.type == 'Workflow':
            self.main = properties['main']

        # This assumes that each .xaml file can be processed as a workflow
        self.workflow_files: Iterable[Workflow] = (
            Workflow(file_path) for file_path in self.get_workflow_files())
