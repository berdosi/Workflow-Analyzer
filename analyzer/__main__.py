"""Entry module for the Analyzer."""

import logging
import os.path
import sys

from analyzer.analyze.project import Project
from analyzer.render.documentation import Documentation

def main(argv):
    """Entry point for the Analyzer: find the target folder, read project, generate output."""
    logging.basicConfig(level=logging.INFO)
    if len(argv) != 1:
        logging.info(
            "No argument passed: assuming parent dictionary to be the input")
        target_dir = os.path.realpath('..')
    else:
        target_dir = argv[0]
    logging.info('Target directory is %s', target_dir)

    project = Project(target_dir)

    Documentation(project)


if __name__ == "__main__":
    main(sys.argv[1:])
