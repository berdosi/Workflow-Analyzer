import xml.etree.ElementTree as ET
import re
from typing import Union

class XamlParser():
    """Common methods used by classes dealing with XAML documents."""

    def _get_attribute(self, attribute_name: str) -> Union[str, None]:
        if attribute_name in self._attribs:
            return self._attribs[attribute_name]
        return None

    def _remove_namespace_from_type_string(self, type_string):
        "Remove namespace annotations from type strings, Element names, etc."
        namespace_regex = re.compile(r'[a-z]+:')
        return namespace_regex.sub('', type_string)

    def _get_annotation(self, element: ET.Element) -> Union[str, None]:
        """Annotation attribute names with their namespaces are just too long."""
        annotation_attrib_name = (
            '{http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation}Annotation.AnnotationText')
        return self._get_attribute(annotation_attrib_name)

    def __init__(self, document: ET.Element):
        self._attribs = document.attrib


class WorkflowArgument(XamlParser):
    """Extract the Argument's properties from the element node"""
    def __init__(self, argument_element: ET.Element):
        self._attribs = argument_element.attrib;
        
        self.annotation = self._get_annotation(argument_element)
        self.name       = self._get_attribute("Name")
        self._raw_type  = self._get_attribute("Type")
        self.direction  = self._get_direction()
        self.type       = self._get_type()

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

    def get_annotation(self) -> str:
        """Get the annotation of the top-level Activity from the file."""
        return self._get_annotation(self._root_activity)

    def get_referenced_workflows(self): # NOT IMPLEMENTED
        """List the paths of the workflow files referenced by this file."""
        raise NotImplementedError

    def get_arguments(self) -> list[WorkflowArgument]:
        """List the Arguments of the workflow."""
        return list(map(
            lambda argNode: WorkflowArgument(argNode),
            self.document
                .findall("./{*}Members/{*}Property")))

    def get_root_activity(self) -> Union[ET.Element, None]:
        """The Activity should have a StateMachine, Flowchart or Sequence as 
        its child."""
        root_activity = self.document.find('./{*}StateMachine')
        if None == root_activity:
            root_activity = self.document.find('./{*}Flowchart')
        if None == root_activity:
            root_activity = self.document.find('./{*}Sequence')
        return root_activity

    def __init__(self, file_path):
        self.file_path = file_path
        self.document = ET.parse(open(file_path))
        self._root_activity = self.get_root_activity()
        self._attribs = self._root_activity.attrib

        self.annotation = self.get_annotation()
        self.arguments = self.get_arguments()
        self.display_name = self._get_attribute('DisplayName')
