"""Test for Workflow()"""

import os
from analyzer.analyze.workflow import Workflow

def test_workflow():
    """Test basic workflow file parsing"""
    workflow_path = os.path.join(os.path.dirname(__file__), 'assets/Main.xaml')
    workflow_instance = Workflow(workflow_path)
    assert workflow_instance.display_name == 'General Business Process'
