# __init__.py
# Author: Thomas MINIER - MIT License 2019
"""
    Lexer and parser utilities for manipulating OTTR template definitions and instances.
"""
from ottr.parsers.stottr.parser import parse_templates_stottr, parse_instances_stottr

__all__ = [
    'parse_templates',
    'parse_instances'
]


def parse_templates(text, format="stottr"):
    """
        Parse a set of stOTTR template definitions.
        Use the format parameter to set the language used to decalred templates (default to pOTTR).
        Formats currently supported: stOTTR
    """
    if format.lower() == 'stottr':
        return parse_templates_stottr(text)
    raise TypeError("Unsupported language '{}'. Only the stOTTR format is currently supported.".format(format))


def parse_instances(text, format="stottr"):
    """
        Parse a set of stOTTR template instances.
        Use the format parameter to set the language used to decalred templates (default to pOTTR).
        Formats currently supported: stOTTR
    """
    if format.lower() == 'stottr':
        return parse_instances_stottr(text)
    raise TypeError("Unsupported language '{}'. Only the stOTTR format is currently supported.".format(format))
