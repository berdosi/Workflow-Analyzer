import os
from analyzer.analyze.workflow import Workflow

def test_workflow():
    workflow_path = os.path.join(os.path.dirname(__file__), 'assets/Main.xaml')
    wf = Workflow(workflow_path)
    assert(wf.display_name == 'General Business Process')