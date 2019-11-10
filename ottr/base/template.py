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
    def expand(self, arguments, all_templates, as_nt=False):
        """Returns a generator that expands the template"""
        pass

    def add_parameter(self, name, position):
        """Register a new template parameter"""
        if position not in self._parameters:
            self._parameters[position] = name

    def format_arguments(self, arguments):
        """Format a list of execution arguments, i.e., a list of tuple (position, value), so that they can be used for template expansion"""
        args = dict()
        for position, value in arguments:
            if position in self._parameters:
                args[self._parameters[position]] = value
            else:
                # TODO do something???
                pass
        return args


class MainTemplate(AbstractTemplate):
    """An OTTR template definition, which contains several instances to expand."""

    def __init__(self, name, instances):
        super(MainTemplate, self).__init__(name)
        self._instances = instances

    def expand(self, arguments, all_templates, as_nt=False):
        """Returns a generator that expands the template"""
        for instance in self._instances:
            # TODO check that all arguments' values are compatibles with the template declaration???
            yield from instance.expand(arguments, all_templates, as_nt=as_nt)

class NonBaseInstance(AbstractTemplate):
    """
        A non-base OTTR Template instance.
    """

    def __init__(self, name, instance_arguments):
        super(NonBaseInstance, self).__init__(name)
        self._instance_arguments = [(x.position, x.value) for x in instance_arguments if x.is_bound]

    def is_base(self):
        """Returns True if the template is a base template, False otherwise"""
        return False

    def expand(self, arguments, all_templates, as_nt=False):
        if self._name in all_templates:
            template = all_templates[self._name]
            # merge new arguments with previous ones
            new_arguments = dict()
            new_arguments.update(arguments)
            new_arguments.update(template.format_arguments(self._instance_arguments))
            # recursively expand the template instance
            yield from template.expand(new_arguments, all_templates, as_nt=as_nt)
        else:
            raise Exception("Cannot expand the unkown OTTR template '{}'".format(self._name.n3()))
