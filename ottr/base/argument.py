# argument.py
# Author: Thomas MINIER - MIT License 2019
from abc import ABC, abstractmethod
from ottr.base.utils import OTTR
from rdflib import URIRef, BNode

class InstanceArgument(ABC):
    """An instance argument, which corresponds to the parameter of a template."""

    def __init__(self, value, position):
        super(InstanceArgument, self).__init__()
        self._value = value
        self._position = position

    def __str__(self):
        return "({}, pos={})".format(self._value, self._position)

    def __repr__(self):
        return self.__str__()

    @property
    def value(self):
        return self._value

    @property
    def position(self):
        return self._position

    @property
    def is_bound(self):
        """Return True if the argument is bound, False otherwise"""
        return False

    @abstractmethod
    def evaluate(self, bindings=dict(), bnode_suffix=0, as_nt=False):
        """Evaluate the argument using an optional set of bindings"""
        pass


class ConcreteArgument(InstanceArgument):
    """An argument that evaluates to a constant RDF term, i.e., a RDF term."""

    def __init__(self, value, position):
        super(ConcreteArgument, self).__init__(value, position)

    @property
    def is_bound(self):
        return True

    def evaluate(self, bindings=dict(), bnode_suffix=(0,0), as_nt=False):
        term = self._value
        if type(term) == BNode and bnode_suffix is not None:
            term = BNode("{}_{}_{}".format(str(term), bnode_suffix[0], bnode_suffix[1]))
        return term.n3() if as_nt else term

class URIArgument(ConcreteArgument):
    """A ConcreteArgument that evaluates to an URI"""

    def __init__(self, uri, position):
        super(URIArgument, self).__init__(URIRef(uri), position)


class VariableArgument(InstanceArgument):
    """A variable argument, i.e., a SPARQL variable"""

    def __init__(self, value, position):
        super(VariableArgument, self).__init__(value, position)

    def evaluate(self, bindings=dict(), bnode_suffix=(0, 0), as_nt=False):
        if self._value in bindings:
            term = bindings[self._value]
            if type(term) == BNode and bnode_suffix is not None:
                term = BNode("{}_{}_{}".format(str(term), bnode_suffix[0], bnode_suffix[1]))
            return term.n3() if as_nt else term
        return OTTR.none
