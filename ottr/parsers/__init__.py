# __init__.py
# Author: Thomas MINIER - MIT License 2019
"""
    Lexer and parser utilities for manipulating OTTR template definitions and instances.
"""
from ottr.parsers.pottr.parser import parse_templates_pottr, parse_instances_pottr

__all__ = [
    'parse_templates',
    'parse_instances'
]


def parse_templates(text, format="pottr"):
    """
        Parse a set of OTTR template definitions.
        Use the format parameter to set the language used to decalred templates (default to pOTTR).
        Formats currently supported: pOTTR
    """
    if format.lower() == 'pottr':
        return parse_templates_pottr(text)
    raise TypeError("Unsupported language '{}'. Only the pOTTR format is currently supported.".format(format))


def parse_instances(text, format="pottr"):
    """
        Parse a set of OTTR template instances.
        Use the format parameter to set the language used to decalred templates (default to pOTTR).
        Formats currently supported: pOTTR
    """
    if format.lower() == 'pottr':
        return parse_instances_pottr(text)
    raise TypeError("Unsupported language '{}'. Only the pOTTR format is currently supported.".format(format))
