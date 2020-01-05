# argument.py
# Author: Thomas MINIER - MIT License 2019-2020
from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from rdflib import BNode, URIRef

from ottr.base.utils import OTTR
from ottr.types import ExpansionResults, InputBindings, Term


class InstanceArgument(ABC):
    """An abstract instance argument, which corresponds to the parameter of a template.

    Args:
      * value: Argument's value.
      * position: Argument's position in the template's parameters list.
    """

    def __init__(self, value: Term, position: int):
        super(InstanceArgument, self).__init__()
        self._value = value
        self._position = position

    def __str__(self) -> str:
        return f"InstanceArgument({self._value}, {self._position})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def value(self) -> Term:
        """The argument's value"""
        return self._value

    @property
    def position(self) -> int:
        """The argument's position in the template's parameters list"""
        return self._position

    @property
    def is_bound(self) -> bool:
        """Return True if the argument is bound (it is not a Variable), False otherwise"""
        return False

    @abstractmethod
    def evaluate(self, bindings: InputBindings = dict(), bnode_suffix: Tuple[int, int] = (0, 0), as_nt: bool = False) -> Iterable[ExpansionResults]:
        """Evaluate the argument using an optional set of bindings.

        Args:
          * bindings: set of bindings used for evaluation.
          * bnode_suffix: Pair of suffixes used for creating unique blank nodes.
          * as_nt: True if the RDF triples produced should be in n-triples format, False to use the rdflib format.

        Yields:
          RDF triples, in rdflib or n-triples format.
        """
        pass


class ConcreteArgument(InstanceArgument):
    """An argument that evaluates to a constant RDF term, i.e., a RDF term.

    Args:
      * value: Argument's value.
      * position: Argument's position in the template's parameters list.
    """

    def __init__(self, value: Term, position: int):
        super(ConcreteArgument, self).__init__(value, position)

    def __str__(self) -> str:
        return f"ConcreteArgument({self._value}, {self._position})"

    @property
    def is_bound(self) -> bool:
        return True

    def evaluate(self, bindings: InputBindings = dict(), bnode_suffix: Tuple[int, int] = (0, 0), as_nt: bool = False) -> Iterable[ExpansionResults]:
        """Evaluate the argument using an optional set of bindings.

        Args:
          * bindings: set of bindings used for evaluation.
          * bnode_suffix: Pair of suffixes used for creating unique blank nodes.
          * as_nt: True if the RDF triples produced should be in n-triples format, False to use the rdflib format.

        Yields:
          RDF triples, in rdflib or n-triples format.
        """
        term = self._value
        if type(term) == BNode and bnode_suffix is not None:
            term = BNode(f"{term}_{bnode_suffix[0]}_{bnode_suffix[1]}")
        return term.n3() if as_nt else term


class URIArgument(ConcreteArgument):
    """A ConcreteArgument that always evaluates to an URI.

    Args:
      * value: Argument's value (an URI).
      * position: Argument's position in the template's parameters list.
    """

    def __init__(self, uri: URIRef, position: int):
        super(URIArgument, self).__init__(URIRef(uri), position)

    def __str__(self) -> str:
        return f"URIArgument({self._value}, {self._position})"


class VariableArgument(InstanceArgument):
    """A variable argument, i.e., a SPARQL variable.

    Args:
      * value: Argument's value (a SPARQL variable).
      * position: Argument's position in the template's parameters list.
    """

    def __init__(self, value: Term, position: int):
        super(VariableArgument, self).__init__(value, position)

    def __str__(self) -> str:
        return f"VariableArgument({self._value}, {self._position})"

    def evaluate(self, bindings: InputBindings = dict(), bnode_suffix: Tuple[int, int] = (0, 0), as_nt: bool = False) -> Iterable[ExpansionResults]:
        """Evaluate the argument using an optional set of bindings.

        Args:
          * bindings: set of bindings used for evaluation.
          * bnode_suffix: Pair of suffixes used for creating unique blank nodes.
          * as_nt: True if the RDF triples produced should be in n-triples format, False to use the rdflib format.

        Yields:
          RDF triples, in rdflib or n-triples format.
        """
        if self._value in bindings:
            term = bindings[self._value]
            if type(term) == BNode and bnode_suffix is not None:
                term = BNode(f"{term}_{bnode_suffix[0]}_{bnode_suffix[1]}")
            return term.n3() if as_nt else term
        return OTTR.none
