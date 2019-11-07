# template.py
# Author: Thomas MINIER - MIT License 2019
from abc import ABC, abstractmethod


class AbstractTemplate(ABC):
    """An abstract OTTR Template."""

    def __init__(self, name):
        super(AbstractTemplate, self).__init__()
        self._name = name
        self._parameters = dict()

    @property
    def name(self):
        return self._name

    @abstractmethod
    def expand(self, parameters, as_nt=False):
        """Returns a generator that expands the template"""
        pass

    def add_parameter(self, name, position):
        """Register a new template parameter"""
        if position not in self._parameters:
            self._parameters[position] = name

    def format_parameters(self, params):
        """Format a list of execution parameters, i.e., a list of tuple (position, value), so that they can be used for template expansion"""
        res = dict()
        for position, value in params:
            if position in self._parameters:
                res[self._parameters[position]] = value
            else:
                # TODO do something???
                pass
        return res


class MainTemplate(AbstractTemplate):
    """An OTTR template definition, which contains several instances to expand."""

    def __init__(self, name, instances):
        super(MainTemplate, self).__init__(name)
        self._instances = instances

    def expand(self, parameters, as_nt=False):
        """Returns a generator that expands the template"""
        for instance in self._instances:
            yield from instance.expand(parameters, as_nt=as_nt)
