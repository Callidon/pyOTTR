# __init__.py
# Author: Thomas MINIER - MIT License 2019
"""
    Lexer and parser utilities for manipulating OTTR template definitions and instances.
"""
from typing import Dict, List, Tuple, Union

from ottr.base.template import AbstractTemplate
from ottr.parsers.stottr.parser import (parse_instances_stottr,
                                        parse_templates_stottr)
from ottr.types import Term

__all__ = [
    'parse_templates',
    'parse_instances'
]


def parse_templates(text: str, format: str = "stottr") -> List[AbstractTemplate]:
    """Parse a set of OTTR template definitions.

    Args:
      * text: Set of OTTR template definitions in text format.
      * format: Format of the input template definitions. Defaults to sOTTR. Supported formats: sOTTR.

    Returns:
      The parsed OTTR template definitions.

    Throws: `TypeError` if the input format is not supported.
    """
    if format.lower() == 'stottr':
        return parse_templates_stottr(text)
    raise TypeError(f"Unsupported language '{format}'. Only the stOTTR format is currently supported.")


def parse_instances(text: str, format: str = "stottr") -> List[Dict[str, Union[Term, List[Tuple[int, Term]]]]]:
    """Parse a set of OTTR template instances.

    Args:
      * text: Set of OTTR instances in text format.
      * format: Format of the input instances. Defaults to sOTTR. Supported formats: sOTTR.

    Returns:
      The parsed OTTR template instances.

    Throws: `TypeError` if the input format is not supported.
    """
    if format.lower() == 'stottr':
        return parse_instances_stottr(text)
    raise TypeError(f"Unsupported language '{format}'. Only the stOTTR format is currently supported.")
