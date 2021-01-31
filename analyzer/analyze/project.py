import glob
import json.decoder
import os.path
from typing import Any
import logging

from analyzer.analyze.workflow import Workflow

class Project():
    def get_project_properties(self, target_dir: str) -> dict[str, Any]:
        project_file = os.path.join(target_dir, 'project.json')
        if os.path.exists(project_file):
            return json.load(open(project_file))
        else:
            raise FileNotFoundError('No project.json found - not a valid project folder.')

    def get_workflow_files(self) -> list[str]:
        return [ file_name 
            for file_name 
            in
                glob.glob(
                    os.path.join(
                        self.project_directory, 
                        './**/*.xaml'),
                    recursive=True)]

    def __init__(self, project_directory):
        logging.basicConfig(level=logging.INFO)
        self.project_directory = project_directory
        self.properties = self.get_project_properties(project_directory)
        self.name = self.properties['name']
        self.version = self.properties['projectVersion']
        self.description = self.properties['description']
        
        if 'projectType' in self.properties:
            self.type = self.properties['projectType']
        else:
            self.type = 'Workflow'

        # Libraries have no Main
        if self.type == 'Workflow':
            self.main = self.properties['main']

        # This assumes that each .xaml file can be processed as a workflow
        self.workflow_files = list(map(
            lambda file_path: Workflow(file_path),
            self.get_workflow_files()))
