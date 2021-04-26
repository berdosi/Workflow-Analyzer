"""Classes representing Workflows, and Workflow parts."""

import re
from typing import Optional, Iterable

import lxml.etree as ET

default_namespaces = {
    "wf": "http://schemas.microsoft.com/netfx/2009/xaml/activities",
    "presentation": "http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation",
    "presentation2010": "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation",
    "this": "clr-namespace:",
    "ui": "http://schemas.uipath.com/workflow/activities",
    "x": "http://schemas.microsoft.com/winfx/2006/xaml",
}

class XamlParser():
    """Common methods used by classes dealing with XAML documents."""
    namespaces = default_namespaces

    def _get_attribute(self, attribute_name: str) -> Optional[str]:
        if attribute_name in self._attribs:
            return self._attribs[attribute_name]
        return None

    def _remove_namespace_from_type_string(self, type_string) -> str:
        "Remove namespace annotations from type strings, Element names, etc."
        namespace_regex = re.compile(r'[a-z]+:')
        return namespace_regex.sub('', type_string)

    def _get_annotation(self, element: ET.Element) -> Optional[str]:
        """Annotation attribute names with their namespaces are just too long."""
        annotation_attrib_name = (
            f'{{{self.namespaces["presentation2010"]}}}Annotation.AnnotationText')
        return self._get_attribute(annotation_attrib_name)

    def __init__(self, document: ET.Element):
        self._attribs = document.attrib

class Variable():
    _element: ET.Element
    data_type: str
    default_value: str
    name: str
    read_only: bool
    annotation: str = ""

    def __init__(self, element: ET.Element, namespaces: dict ={}):
        self._element = element
        self.data_type = self._get_attribute(f'{{{namespaces["x"]}}}TypeArguments')
        self.default_value = self._get_attribute(f'Default')
        self.name = self._get_attribute(f'Name')
        self.annotation = self._get_attribute(f'{{{namespaces["presentation2010"]}}}Annotation.AnnotationText')
    
    def _get_attribute(self, attribute_name: str, fallback_value: str = ""):
        attrib = self._element.attrib
        if attribute_name in attrib:
            return attrib[attribute_name]
        return fallback_value
    
    def __str__(self):
        return f'<Variable "{self.name}" ({self.data_type}) = "{self.default_value.splitlines()[0]}...">'

class WorkflowArgument(XamlParser):
    """Extract the Argument's properties from the element node"""
    def __init__(self, argument_element: ET.Element, root_element: ET.Element, namespaces= {}):
        self._attribs = argument_element.attrib
        
        self.annotation = self._get_annotation(argument_element)
        self.name       = self._get_attribute("Name")
        self._raw_type  = self._get_attribute("Type")
        self.direction  = self._get_direction()
        self.type       = self._get_type()
        
        # get default value
        if self.direction == ArgumentDirection.in_arg:
            default_value = [x 
                for x in root_element.attrib 
                if x.endswith(f'.{self.name}') 
                    and x.startswith('{clr-namespace:}')]
            if len(default_value) > 0:
                self.default_value = default_value[0]

    def _get_direction(self) -> str:
        if self._raw_type.startswith('InArgument'):
            return ArgumentDirection.in_arg
        if self._raw_type.startswith('OutArgument'):
            return ArgumentDirection.out_arg
        if self._raw_type.startswith('InOutArgument'):
            return ArgumentDirection.inout_arg

    def _get_type(self) -> str:
        type_regex = re.compile(r'^[OIntu]+Argument\((.*)\)$')
        argmatch = type_regex.match(self._raw_type)
        if argmatch is None:
            raise ValueError
        return self._remove_namespace_from_type_string(argmatch.group(1))

    def __str__(self):
        return f'{self.name, self.direction, self.type}'

class ArgumentDirection():
    """Enumerates possible argument directions."""
    in_arg = "In"
    out_arg = "Out"
    inout_arg = "InOut"

class Workflow(XamlParser):
    """Represents a workflow file from the project"""

    ns = default_namespaces

    def get_annotation(self) -> str:
        """Get the annotation of the top-level Activity from the file."""
        return self._get_annotation(self._root_activity)

    def get_referenced_workflows(self) -> Iterable[str]:
        """List the paths of the workflow files referenced by this file."""
        invoke_activities = self.get_root_activity().iterfind('.//ui:InvokeWorkflowFile', self.ns)
        return map(
            lambda invoke_activity: str(invoke_activity.attrib['WorkflowFileName']).replace('\\', '/'),
            invoke_activities)

    def get_arguments(self) -> Iterable[WorkflowArgument]:
        """List the Arguments of the workflow."""
        return map(
            lambda argNode: WorkflowArgument(argNode, self.document.getroot()),
            self.document.iterfind(
                "./x:Members/x:Property",
                namespaces=self.ns))

    def get_variables(self) -> Iterable[Variable]:
        return map(
            lambda varNode: Variable(varNode, self.ns),
            self.document.iterfind(
                './/wf:Variable',
                namespaces=self.ns))

    def get_root_activity(self) -> Optional[ET.Element]:
        """The Activity should have a StateMachine, Flowchart or Sequence as its child.
        
        This is usually a Sequence, Flowcart, or StateMachine, however other root elements are possible.
        As finding all of them is not in scope for now, this activity detects the first one that doesn't contain
        'TextExpression' instead.
        """
        toplevel_elements = self.document.iterfind('./wf:*', namespaces=self.ns)
        for child in toplevel_elements:
            if not 'TextExpression' in child.tag:
                return child
        return None

    def __init__(self, file_path):
        self.file_path = file_path
        self.document: ET = ET.parse(open(file_path))
        self._root_activity = self.get_root_activity()
        self._attribs = self._root_activity.attrib

        self.annotation = self.get_annotation()
        self.arguments = self.get_arguments()
        self.variables = self.get_variables()
        self.referenced_workflows = self.get_referenced_workflows()
        self.display_name = self._get_attribute('DisplayName')
