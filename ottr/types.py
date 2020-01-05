# types.py
# Author: Thomas MINIER - MIT License 2019-2020
"""This module contains common types encountered in the ottr package.

  They are used for type annotations, as specified by PEP 484, PEP 526,
  PEP 544, PEP 586, PEP 589, and PEP 591.
"""
from typing import Dict, List, Tuple, Union

from rdflib import BNode, Literal, URIRef, Variable

Term = Union[BNode, Literal, URIRef, Variable]

BoundedTerm = Union[BNode, Literal, URIRef]

Triple = Tuple[BoundedTerm, BoundedTerm, BoundedTerm]

StrTriple = Tuple[str, str, str]

ExpansionResults = Union[Triple, StrTriple]

InputBindings = Dict[Variable, Union[Term, List[Term]]]
