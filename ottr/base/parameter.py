# parameter.py
# Author: Thomas MINIER - MIT License 2019
from abc import ABC, abstractmethod
from ottr.base.utils import OTTR

class InstanceParameter(ABC):
    """An instance parameter"""

    def __init__(self, value, constraints=list()):
        super(Parameter, self).__init__()
        self._value = value
        self._constraints = constraints

    def update_constraints(new_constraints):
        """Update the list of current constraints with new ones"""
        self._constraints += constraints

    @abstractmethod
    def evaluate(self, bindings=dict()):
        """Evaluate the parameter using an optional set of bindings"""
        pass


class ConcreteParameter(InstanceParameter):
    """An instance that evaluates to a constant, i.e., a RDF term."""

    def __init__(self, value, constraints=list()):
        super(ConcreteParameter, self).__init__(value, constraints)

    def evaluate(self, bindings=dict()):
        return self._value


class VariableParameter(object):
    """A variable parameter, i.e., a SPARQL variable"""

    def __init__(self, value, constraints=list()):
        super(VariableParameter, self).__init__(value, constraints)

    def evaluate(self, bindings=dict()):
        if self._value in bindings:
            # TODO add constraints checking
            return bindings[self._value]
        return OTTR('none')
