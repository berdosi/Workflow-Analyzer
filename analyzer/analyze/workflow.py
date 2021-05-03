"""Classes representing Workflows, and Workflow parts."""

import re
from dataclasses import dataclass
from typing import Optional, Iterable, Callable, Dict

import lxml.etree as ET

default_namespaces = {
    "wf": "http://schemas.microsoft.com/netfx/2009/xaml/activities",
    "presentation": "http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation",
    "presentation2010": "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation",
    "this": "clr-namespace:",
    "ui": "http://schemas.uipath.com/workflow/activities",
    "x": "http://schemas.microsoft.com/winfx/2006/xaml",
}

@dataclass
class XamlParser():
    """Common methods used by classes dealing with XAML documents."""
    namespaces = default_namespaces
    _attribs: dict()

    def _get_attribute(self, attribute_name: str) -> Optional[str]:
        """Get an attribute in a nullable manner."""
        if attribute_name in self._attribs:
            return self._attribs[attribute_name]
        return None

    @staticmethod
    def _remove_namespace_from_type_string(type_string) -> str:
        "Remove namespace annotations from type strings, Element names, etc."
        namespace_regex = re.compile(r'[a-z]+:')
        return namespace_regex.sub('', type_string)

    def _get_annotation(self) -> Optional[str]:
        """Annotation attribute names with their namespaces are just too long."""
        annotation_attrib_name = (
            f'{{{self.namespaces["presentation2010"]}}}Annotation.AnnotationText')
        return self._get_attribute(annotation_attrib_name)

@dataclass
class Variable():
    """Represents Variable in a workflow for further analysis."""
    _element: ET.Element
    data_type: str
    default_value: str
    name: str
    read_only: bool
    annotation: str = ""

    def __init__(self, element: ET.Element, namespaces: dict = None):
        if namespaces is None:
            namespaces = {}

        self._element = element
        self.data_type = self._get_attribute(f'{{{namespaces["x"]}}}TypeArguments')
        self.default_value = self._get_attribute('Default')
        self.name = self._get_attribute('Name')
        self.annotation = self._get_attribute(
            f'{{{namespaces["presentation2010"]}}}Annotation.AnnotationText')

    def _get_attribute(self, attribute_name: str, fallback_value: str = ""):
        attrib = self._element.attrib
        if attribute_name in attrib:
            return attrib[attribute_name]
        return fallback_value

    def __str__(self):
        first_line = self.default_value.splitlines()[0]
        return f'<Variable "{self.name}" ({self.data_type}) = "{first_line}...">'

@dataclass
class WorkflowArgument(XamlParser):
    """Extract the Argument's properties from the element node"""
    def __init__(self, argument_element: ET.Element, root_element: ET.Element,
            namespaces: Dict[str, str] = None):
        if namespaces is None:
            namespaces = {}
        super().__init__(argument_element)
        self._attribs = argument_element.attrib

        self.annotation = self._get_annotation()
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
        raise ValueError

    def _get_type(self) -> str:
        type_regex = re.compile(r'^[OIntu]+Argument\((.*)\)$')
        argmatch = type_regex.match(self._raw_type)
        if argmatch is None:
            raise ValueError
        return self._remove_namespace_from_type_string(argmatch.group(1))

    def __str__(self):
        return f'{self.name, self.direction, self.type}'

@dataclass
class ArgumentDirection():
    """Enumerates possible argument directions."""
    in_arg = "In"
    out_arg = "Out"
    inout_arg = "InOut"

@dataclass
class Workflow(XamlParser):
    """Represents a workflow file from the project"""

    default_namespaces = default_namespaces

    def get_annotation(self) -> Optional[str]:
        """Get the annotation of the top-level Activity from the file."""
        return self._get_annotation()

    def get_referenced_workflows(self) -> Iterable[str]:
        """List the paths of the workflow files referenced by this file."""
        invoke_activities = self.get_root_activity().iterfind(
            './/ui:InvokeWorkflowFile',
            self.default_namespaces)
        return map(
            lambda invoke_activity:
                str(invoke_activity.attrib['WorkflowFileName']).replace('\\', '/'),
            invoke_activities)

    def get_arguments(self) -> Iterable[WorkflowArgument]:
        """List the Arguments of the workflow."""
        return map(
            lambda argNode: WorkflowArgument(argNode, self.document.getroot()),
            self.document.iterfind(
                "./x:Members/x:Property",
                namespaces=self.default_namespaces))

    def get_variables(self) -> Iterable[Variable]:
        """List Variables for further analysys."""
        return map(
            lambda varNode: Variable(varNode, self.default_namespaces),
            self.document.iterfind(
                './/wf:Variable',
                namespaces=self.default_namespaces))

    def get_root_activity(self) -> Optional[ET.Element]:
        """The Activity should have a StateMachine, Flowchart or Sequence as its child.

        This is usually a Sequence, Flowcart, or StateMachine, however other root elements
        are possible. Finding all of them is not in scope for now, this activity detects
        the first one that doesn't contain 'TextExpression' instead.
        """
        toplevel_elements = self.document.iterfind('./wf:*', namespaces=self.default_namespaces)
        for child in toplevel_elements:
            if not 'TextExpression' in child.tag:
                return child
        return None

    def get_elements_with_selectors(self) -> Iterable[ET.Element]:
        """Find the elements on which the selector checks may be done.

        These elements may be Target attribute of an activity.

        In this case, return the first ancestor for which the name doesn't end with Target.
        """

        elements_with_selectors: Iterable[ET.Element] = self.document.findall('.//*[@Selector]')
        is_target: Callable[[], bool] = lambda element: element.tag.endswith('Target')

        return map(
            lambda element: (element
                if not is_target(element)
                else (ancestor
                    for ancestor in element.iterancestors()
                    if not is_target(ancestor)).__next__()),
            elements_with_selectors)

    def __init__(self, file_path: str):
        self.file_path = file_path
        parser = ET.XMLParser(recover=True, resolve_entities=False)
        self.document: ET = ET.parse(open(file_path), parser=parser)
        self._root_activity = self.get_root_activity()
        self._attribs = self._root_activity.attrib

        self.display_name = self._get_attribute('DisplayName')
