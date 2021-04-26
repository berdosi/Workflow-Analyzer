"""Review the project based on the validationRules.json file contained in its root.

If it is not available, fall back to validationRules.json in the current module's folder.
"""

from analyzer.analyze.project import Project

class Review():
    """Perform review. Generate XML output into deliverables, and verbose output on the
    terminal. In case the review is failed, error is raised."""
    VALIDATION_FILE_NAME = "validationRules.json"

    def __init__(self, project: Project):
        pass

    def write_deliverable(self) -> None:
        """Write the results as XML files to be picked up  by CI/CD tools"""

    def write_terminal_output(self) -> None:
        """Write the results to the terminal."""
