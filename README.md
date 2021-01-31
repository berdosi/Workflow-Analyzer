#   Workflow-Analyzer

Workflow Analizer for CI Engines for UiPath projects.

To be used as part of a CI Pipeline:
-   Copy this project's folder into the Workflow Foundation project's folder.
-   Run the script in this project's root. Alternatively, a folder may be passed as an argument. `python3 -m analyzer`

The analysis deliverables will be placed in the `/deliverables` folder.

Plans:
-   [x] Generate documentation
    -   [x] Workflow files
        -   [x] Name
        -   [x] Annotation
        -   [x] Arguments
            -   [x] Name
            -   [x] Direction
            -   [x] Type
            -   [x] Annotation
            -   [ ] Default Value
-   [ ] Workflow analysis
    -   [ ] Naming Convention
        -   [ ] Workflow
        -   [ ] Argument
        -   [ ] Variable
    -   [ ] Workflow Checks
        -   [ ] Not empty
        -   [ ] Has annnotation
        -   [ ] Referenced by other workflow, or public workflow of a Library
        -   [ ] Deeply nested ifs and workflows
    -   [ ] Selectors
        -   [ ] Too lax: idx, wildcard, regex
        -   [ ] Not valid XML
    -   [ ] Activities
        -   [ ] Delay
        -   [ ] Invoke Code, VBScript, PowerShell, Macro, JavaScript
        -   [ ] Default Names
            -   [ ] e.g. for Log Message, If, Sequence, Assign, Multiple Assign, For Each, Flowchart, Do While, Try Catch

