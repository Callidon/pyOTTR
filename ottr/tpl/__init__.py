# __init__.py
# Author: Thomas MINIER - MIT License 2019
"""
    OTTR template library, available in RDF format at http://tpl.ottr.xyz/
"""

from ottr.tpl.rdf import RDF_TEMPLATES
from ottr.tpl.rdfs import RDFS_TEMPLATES

__all__ = [
    'RDFS_TEMPLATES',
    'RDF_TEMPLATES'
]
