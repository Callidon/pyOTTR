# template.py
# Author: Thomas MINIER - MIT License 2019
from abc import ABC, abstractmethod
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import RDFS
from ottr.base.utils import OTTR_IRI, OTTR_NONE

class TemplateParameter(object):
    """The parameter of an OTTR Template"""

    def __init__(self, name, param_type, optional, nonblank):
        super(TemplateParameter, self).__init__()
        self._name = name
        self._param_type = param_type
        self._optional = optional
        self._nonblank = nonblank

    @property
    def name(self):
        """Get the parameter name, i.e., a SPARQL variable"""
        return self._name

    def __str__(self):
        res = "{} {}".format(self._param_type.n3(), self._name.n3())
        if self._optional:
            res = "? " + res
        if self._nonblank:
            res = "! " + res
        return res

    def __repr__(self):
        return self.__str__()

    def validate(self, value):
        """Assert that an argument can be used for this parameter, i.e., its value is compatible with the parameter definition (type, optional, non blank, etc)"""
        # assert that the argument's type is correct
        if self._param_type != RDFS.Resource:
            # validate uris
            if self._param_type == OTTR_IRI and type(value) != URIRef:
                return False, "expected an IRI but instead got a {}".format(type(value))
            elif type(value) == Literal and value.datatype != self._param_type:
                return False, "expected a Literal with datatype {} but instead got {}".format(self._param_type.n3(), value.datatype)
        # assert that a non-optional parameter cannot be bound to ottr:None
        if not self._optional and value == OTTR_NONE:
            return False, 'this parameter is not optional, so it cannot be bound to ottr:none.'
        # assert that a non blank parameter is not bound to a blank node
        if self._nonblank and type(value) == BNode:
            return False, 'this parameter is non blank, so it cannot be bound to a blank node.'
        return True, None

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

    def add_parameter(self, name, position, param_type=RDFS.Resource, optional=False, nonblank=False):
        """Register a new template parameter"""
        if position not in self._parameters:
            self._parameters[position] = TemplateParameter(name, param_type, optional, nonblank)

    def format_arguments(self, arguments):
        """Format a list of execution arguments, i.e., a list of tuple (position, value), so that they can be used for template expansion"""
        args = dict()
        for position, value in arguments:
            if position in self._parameters:
                # validate that the argument can be used for this parameter
                is_valid, error_reason = self._parameters[position].validate(value)
                if is_valid:
                    args[self._parameters[position].name] = value
                else:
                    # TODO report/raise exception ??
                    raise Exception("Invalid argument {} used for parameter \"{}\". Reason : {} ".format(value.n3(), self._parameters[position], error_reason))
            else:
                raise Exception("Missing argument in position {} in template {}".format(position, self._name.n3()))
        return args


class MainTemplate(AbstractTemplate):
    """An OTTR template definition, which contains several instances to expand."""

    def __init__(self, name, instances):
        super(MainTemplate, self).__init__(name)
        self._instances = instances

    def expand(self, arguments, all_templates, as_nt=False):
        """Returns a generator that expands the template"""
        for instance in self._instances:
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
