# template.py
# Author: Thomas MINIER - MIT License 2019
from abc import ABC, abstractmethod


class AbstractTemplate(ABC):
    """An abstract OTTR Template."""

    def __init__(self, name):
        super(AbstractTemplate, self).__init__()
        self._name = name

    @abstractmethod
    def expand(self, parameters, as_nt=False):
        """Returns a generator that expands the template"""
        pass


class MainTemplate(AbstractTemplate):
    """An OTTR template definition, which contains several instances to expand."""

    def __init__(self, name, instances):
        super(MainTemplate, self).__init__(name)
        self._instances = instances

    def expand(self, parameters, as_nt=False):
        """Returns a generator that expands the template"""
        for instance in self._instances:
            yield from instance.expand(parameters, as_nt=as_nt)
