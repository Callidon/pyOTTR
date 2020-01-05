# template.py
# Author: Thomas MINIER - MIT License 2019
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional, Tuple, Any, List

from rdflib import BNode, Literal, URIRef, Variable
from rdflib.namespace import RDFS

from ottr.base.argument import InstanceArgument

from ottr.base.utils import OTTR_IRI, OTTR_NONE
from ottr.types import BoundedTerm, ExpansionResults, InputBindings


class TemplateParameter(object):
    """The parameter of an OTTR Template.

    Args:
      * name: The parameter's name.
      * param_type: The parameter's type.
      * optional: if the parameter is optional or not.
      * nonblank: if the parameter accepts blank node or not.
      * default: the parameter's default value if it is set to `ottr:None`.
    """

    def __init__(self, name: Variable, param_type: str, optional: bool, nonblank: bool, default: BoundedTerm = None):
        super(TemplateParameter, self).__init__()
        self._name = name
        self._param_type = param_type
        self._optional = optional
        self._nonblank = nonblank
        self._default = default
        # parameter with a default value are automatically set to optional
        if default is not None:
            self._optional = True

    @property
    def name(self) -> Variable:
        """Get the parameter name, i.e., a SPARQL variable"""
        return self._name

    def __str__(self) -> str:
        res = f"{self._param_type.n3()} {self._name.n3()}"
        if self._optional:
            res = "? " + res
        if self._nonblank:
            res = "! " + res
        return res

    def __repr__(self) -> str:
        return self.__str__()

    def validate(self, value: BoundedTerm) -> Tuple[bool, Optional[BoundedTerm], Optional[str]]:
        """Assert that a RDF Term can be used as argument for this parameter, *i.e.*, its value is compatible with the parameter definition (type, optional, non blank, etc).

        Argument: The value to validate.

        Returns: A tuple (`is_valid`, `value`, `error_reason`) where:
          * `is_valid` is a boolean which indicates the outcome of the validation.
          * `value` is the RDF value to use for the argument. Set to `None` if the validation was not successfull.
          * `error_reason` is an error message that indicates why the validation has failed. Set to `None` if the validation was successfull.
        """
        # assert that the argument's type is correct
        if self._param_type != RDFS.Resource:
            # validate uris
            if self._param_type == OTTR_IRI and (type(value) == Literal or type(value) == Variable):
                return False, None, "expected an IRI but instead got a {}".format(type(value))
            elif type(value) == Literal and value.datatype != self._param_type:
                return False, None, "expected a Literal with datatype {} but instead got {}".format(self._param_type.n3(), value.datatype)
        # assert that a non-optional parameter cannot be bound to ottr:None
        if not self._optional and value == OTTR_NONE:
            return False, None, 'this parameter is not optional, so it cannot be bound to ottr:none.'
        # assert that a non blank parameter is not bound to a blank node
        if self._nonblank and type(value) == BNode:
            return False, None, 'this parameter is non blank, so it cannot be bound to a blank node.'
        # if the value is None but has a default value, use the default value
        if value == OTTR_NONE and self._default is not None:
            return True, self._default, None
        # otherwise, everything is fine :-)
        return True, value, None


class AbstractTemplate(ABC):
    """An abstract OTTR Template.

    Argument: The template's name as an RDF URI.
    """

    def __init__(self, name: URIRef):
        super(AbstractTemplate, self).__init__()
        self._name = name
        self._parameters = dict()

    @property
    def name(self) -> URIRef:
        return self._name

    @abstractmethod
    def expand(self, arguments: InputBindings, all_templates: Dict[URIRef, Any], bnode_suffix: Tuple[int, int] = (0, 0), as_nt: bool = False) -> Iterable[ExpansionResults]:
        """Expands the template and yields RDF triples.

        Args:
          * arguments: Template instantation arguments.
          * all_templates: Map of all templates known at expansion times.
          * bnode_suffix: Pair of suffixes used for creating unique blank nodes.
          * as_nt: True if the RDF triples produced should be in n-triples format, False to use the rdflib format.

        Yields:
          RDF triples, in rdflib or n-triples format.
        """
        pass

    def is_base(self) -> bool:
        """Returns True if the template is a base template, False otherwise"""
        return False

    def add_parameter(self, name: Variable, position: int, param_type: URIRef = RDFS.Resource, optional: bool = False, nonblank: bool = False, default: BoundedTerm = None) -> None:
        """Register a new parameter for this template.

        Args:
          * name: The parameter's name.
          * position: The parameter's position in the template definition.
          * param_type: The parameter's type (an URI). Defaults to `rdfs:Resource`.
          * optional: If the parameter is optional or not. Defaults to `False`.
          * nonblank: If the parameter accepts blank nodes or not. Defaults to `False`.
          * default: The parameter's default value if it is set to `ottr:None`.

        Example:
          >>> from rdflib import Literal, URIRref, Variable
          >>> from rdflib.namespace import Namespace, XSD
          >>> template.add_parameter(Variable("?uri"), 0, param_type=URIRef("http://ns.ottr.xyz/0.4/IRI"), nonblank=True)
          >>> template.add_parameter(Variable("?name"), 1, param_type=XSD.string, nonblank=True)
        """
        if position not in self._parameters:
            self._parameters[position] = TemplateParameter(name, param_type, optional, nonblank, default=default)

    def format_arguments(self, arguments: List[Tuple[int, BoundedTerm]]) -> Dict[Variable, BoundedTerm]:
        """Format a list of expansion arguments so that they can be used for template expansion using the `expand()` method.

        Args: List of expansion arguments.

        Returns: Formatted list of expansion arguments, to be used with the expand() method.

        Example:
          >>> from rdflib import Literal, URIRef
          >>> from rdflib.namespace import XSD
          >>> raw_arguments = [ (0, URIRef("http://example.org#Anna")), (1, Literal("Anna")) ]
          >>> arguments = template.format_arguments(raw_arguments)
          >>> for triple in template.expand(arguments):
          >>>   print(triple)
        """
        args = dict()
        for position, value in arguments:
            if position in self._parameters:
                # validate that the argument can be used for this parameter
                is_valid, v, error_reason = self._parameters[position].validate(value)
                if is_valid:
                    args[self._parameters[position].name] = v
                else:
                    # TODO report/raise exception ??
                    raise Exception("Invalid argument {} used for parameter \"{}\". Reason : {} ".format(value.n3(), self._parameters[position], error_reason))
            else:
                raise Exception("Missing argument in position {} in template {}".format(position, self._name.n3()))
        return args


class MainTemplate(AbstractTemplate):
    """An OTTR template definition, which contains several instances to expand.

    Args:
      * name: The template name.
      * instances: Instances declared in the template.
    """

    def __init__(self, name: URIRef, instances: List[AbstractTemplate]):
        super(MainTemplate, self).__init__(name)
        self._instances = instances

    def __str__(self) -> str:
        instances = ',\n'.join(map(lambda i: str(i), self._instances))
        params = ', '.join(map(lambda i: str(i), self._parameters))
        return f"{self.name}({params}) :: {{\n {instances} }}."

    def __repr__(self) -> str:
        return self.__str__()

    def expand(self, arguments: InputBindings, all_templates: Dict[URIRef, Any], bnode_suffix: Tuple[int, int] = (0, 0), as_nt: bool = False) -> Iterable[ExpansionResults]:
        """Expands the template and yields RDF triples.

        Args:
          * arguments: Template instantation arguments.
          * all_templates: Map of all templates known at expansion times.
          * bnode_suffix: Pair of suffixes used for creating unique blank nodes.
          * as_nt: True if the RDF triples produced should be in n-triples format, False to use the rdflib format.

        Yields:
          RDF triples, in rdflib or n-triples format.
        """
        for instance in self._instances:
            yield from instance.expand(arguments, all_templates, bnode_suffix=bnode_suffix, as_nt=as_nt)


class NonBaseInstance(AbstractTemplate):
    """A non-base OTTR Template instance.

    Args:
      * name: The template name.
      * instance_arguments: Arguments of the template.
    """

    def __init__(self, name: URIRef, instance_arguments: List[InstanceArgument]):
        super(NonBaseInstance, self).__init__(name)
        # store bound & unbound instance arguments separately
        self._bound_arguments = [(x.position, x.value) for x in instance_arguments if x.is_bound]
        self._unbound_arguments = [(x.position, x.value) for x in instance_arguments if not x.is_bound]

    def expand(self, arguments: InputBindings, all_templates: Dict[URIRef, Any], bnode_suffix: Tuple[int, int] = (0, 0), as_nt: bool = False) -> Iterable[ExpansionResults]:
        """Expands the template and yields RDF triples.

        Args:
          * arguments: Template instantation arguments.
          * all_templates: Map of all templates known at expansion times.
          * bnode_suffix: Pair of suffixes used for creating unique blank nodes.
          * as_nt: True if the RDF triples produced should be in n-triples format, False to use the rdflib format.

        Yields: RDF triples, in rdflib or n-triples format.

        Throws: `Exception` when an undefined OTTR template is encountered.
        """
        # increment the bnode unique prefixes, used to unify blank node acrros instance expansions
        bnode_suffix = (bnode_suffix[0], bnode_suffix[1] + 1)
        if self._name in all_templates:
            # fetch template
            template = all_templates[self._name]
            # try to link unbound instance arguments using the given arguments
            args = list(self._bound_arguments)
            for position, value in self._unbound_arguments:
                if value in arguments:
                    args.append((position, arguments[value]))
                else:
                    # TODO raise something ??
                    pass
            # prepare new arguments for recursive template expansion
            new_arguments = dict()
            new_arguments.update(arguments)
            new_arguments.update(template.format_arguments(args))
            # recursively expand the template instance
            yield from template.expand(new_arguments, all_templates, bnode_suffix=bnode_suffix, as_nt=as_nt)
        else:
            raise Exception("Cannot expand the unkown OTTR template '{}'".format(self._name.n3()))
