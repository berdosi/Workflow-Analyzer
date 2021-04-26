"""Review the project based on the validationRules.json file contained in its root.

If it is not available, fall back to validationRules.json in the current module's folder.
"""

from analyzer.analyze.project import Project

class Review():
    VALIDATION_FILE_NAME = "validationRules.json"

    def __init__(self, project: Project):
        pass