# generator.py
# Author: Thomas MINIER - MIT License 2019
from typing import Dict, List, Tuple, Iterable

from rdflib import URIRef, Variable

from ottr.base.template import AbstractTemplate
from ottr.parsers import parse_instances, parse_templates
from ottr.tpl import RDF_TEMPLATES, RDFS_TEMPLATES
from ottr.types import BoundedTerm, Triple


class OttrInstances(object):
    """Compiled OTTR instances, ready to be executed to produce RDF triples.

    Args:
      * exec_id: ID of the execution, used to unify blank nodes generation during template expansion.
      * to_execute: List of tuple (template, instance arguments) to execute.
      * all_templates: Map of all OTTR templates available at execution.
    """

    def __init__(self, exec_id: int, to_execute: List[Tuple[AbstractTemplate, Dict[Variable, BoundedTerm]]], all_templates: Dict[URIRef, AbstractTemplate]):
        super(OttrInstances, self).__init__()
        self._id = exec_id
        self._to_execute = to_execute
        self._all_templates = all_templates

    def execute(self, as_nt: bool = False) -> Iterable[Triple]:
        """Execute the instances to produce RDF triples.

        Args:
          * as_nt: (optional) True if the results should be produced in n-triples format, False if they should be produced in RDFlib format.

        Yields:
            RDF triples, in n-triples or rdflib format.
        """
        for template, params in self._to_execute:
            yield from template.expand(params, self._all_templates, bnode_suffix=(self._id, 0), as_nt=as_nt)


class OttrGenerator(object):
    """An OttrGenerator can load OTTR templates definitions and expand them to produce RDF triples.

    Args:
      * load_defaults: True if default templates library should be loaded, False otherwise.

    Example:
      >>> generator = OttrGenerator()
      >>> generator.load_templates("<http://example.org#Person> [ottr:IRI ?uri, ?firstName] :: { ottr:Triple (?uri, foaf:firstName, ?firstName ) } .")
      >>> generator.instanciate('<http://example.org#Person>(_:person, "Ann"@en)')
      >>> for triple in instances.execute(as_nt=True):
      >>>   print(triple)
    """

    def __init__(self, load_defaults: bool = True):
        super(OttrGenerator, self).__init__()
        self._templates: Dict[URIRef, AbstractTemplate] = dict()
        # counter used for generating instance unique IDs
        self._instance_id = -1
        if load_defaults:
            self.load_templates(RDF_TEMPLATES, format="stottr")
            self.load_templates(RDFS_TEMPLATES, format="stottr")

    def load_templates(self, text: str, format: str = "stottr") -> None:
        """Load a set of OTTR template definitions.

        Args:
          * text: Set of OTTR template definitions in text format.
          * format: Format of the input template definitions. Defaults to sOTTR. Supported formats: sOTTR.

        Throws: `TypeError` if the input format is not supported.
        """
        for template in parse_templates(text, format=format):
            self._templates[template.name] = template

    def instanciate(self, text: str, format: str = "stottr") -> OttrInstances:
        """Instance a set of OTTR instances.

        Args:
          * text: Set of OTTR instances in text format.
          * format: Format of the input instances. Defaults to sOTTR. Supported formats: sOTTR.

        Returns:
          An instance of OttrInstances, that can be executed to generate RDF triples.

        Throws: `TypeError` if the input format is not supported.
        """
        # increment the instance ID generator
        self._instance_id += 1
        # parse instances
        instances = parse_instances(text, format=format)
        # create pairs of (instance, related template)
        to_execute = list()
        for instance in instances:
            if instance['name'] in self._templates:
                template = self._templates[instance['name']]
                exec_parameters = template.format_arguments(instance['arguments'])
                to_execute.append((template, exec_parameters))
            else:
                # TODO report error but do not crash??
                pass
        return OttrInstances(self._instance_id, to_execute, self._templates)
