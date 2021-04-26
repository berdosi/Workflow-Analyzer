"""
Generate documentation for a UiPath project based on the annotations 
within the files.

Create a folder deliverables/documentation, renders the contents in HTML. 
"""

import logging
import os
import re
import typing
from html import escape as e
from analyzer.analyze.project import Project
from analyzer.analyze.workflow import Workflow, WorkflowArgument

TARGET_DIR  = './deliverables/documentation'
TARGET_FILE = 'Documentation.html'

OUTPUT_TEMPLATE = """<!doctype html>
<html>
    <head>
        <meta charset='utf-8'>
        <title>{0} - Documentation</title>
        <style>
            .annotation {{
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>{0}</h1>
            <p>Version: {1}</p>
            <p class='description'>{2}</p>
        </header>
        <main>
            {3}
            {4}
        </main>
    </body>
</html>
"""

OUTPUT_TEMPLATE_WF = """<h2>{0}</h2>
<p>File name: {1}</p>
<p class='annotation'>{2}</p>
<h3>Arguments</h3>
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Direction</th>
            <th>Type</th>
            <th>Annotation</th>
        </tr>
    </thead>
    <tbody>
{3}
    </tbody>
</table>
"""

OUTPUT_TEMPLATE_ARG = """
        <tr>
            <td>{0}</td>
            <td>{1}</td>
            <td>{2}</td>
            <td class='annotation'>{3}</td>
        </tr>
"""

OUTPUT_TEMPLATE_LINE = """<p>{0}</p>
"""

class Documentation():
    def make_directory(self):
        # assume there is no such file
        if not os.path.isdir(TARGET_DIR):
            os.mkdir(TARGET_DIR)

    def render_arguments(self, arguments: list[WorkflowArgument]):
        render_argument = lambda arg: OUTPUT_TEMPLATE_ARG.format(
            e(arg.name),
            e(arg.direction),
            e(arg.type),
            e(arg.annotation if arg.annotation != None else ""))
        return str.join('', map(render_argument, arguments))

    def render_workflow_documentation(self, workflow: Workflow):
        if workflow != None:
            annotation = workflow.annotation if workflow.annotation != None else ""
            return OUTPUT_TEMPLATE_WF.format(
                e(workflow.display_name or ""),
                e(workflow.file_path),
                e(annotation),
                self.render_arguments(workflow.arguments))
        return ""

    def get_main_workflow(self) -> Workflow:
        if self.project.main != None:
            main_workflow_path = os.path.normpath(os.path.join(
                self.project.project_directory, self.project.main))
            for wf in self.project.workflow_files:
                if main_workflow_path ==  os.path.normpath(wf.file_path):
                    return wf
        return None

    def build_documentation(self):
        with open(self.target_path, 'w') as fp:
            main_workfow: Workflow = self.get_main_workflow()
            fp.write(OUTPUT_TEMPLATE.format(
                e(self.project.name),
                e(self.project.version),
                e(self.project.description),
                self.render_workflow_documentation(main_workfow),
                str.join(
                    '',
                    [ self.render_workflow_documentation(wf) 
                        for wf in self.project.workflow_files
                        if wf.file_path != main_workfow.file_path])
            ))

    def __init__(self, project: Project):
        logging.info(project.name)
        self.project = project

        self.make_directory()
        self.target_path = os.path.join(TARGET_DIR, TARGET_FILE)
        self.build_documentation()
