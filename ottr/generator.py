# generator.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers import parse_templates, parse_instances
from ottr.tpl import RDF_TEMPLATES, RDFS_TEMPLATES
from rdflib import URIRef, Variable, Literal

class OttrGenerator(object):
    """
        An OttrGenerator can load OTTR templates definitions and expand them to produce RDF triples.
    """

    def __init__(self, load_defaults=True):
        super(OttrGenerator, self).__init__()
        self._templates = dict()
        # counter used for generating instance unique IDs
        self._instance_id = -1
        if load_defaults:
            self.load_templates(RDF_TEMPLATES, format="stottr")
            self.load_templates(RDFS_TEMPLATES, format="stottr")

    def load_templates(self, text, format="stottr"):
        """
            Load a set of OTTR template definitions.

            Arguments:
                - text ``str``: OTTR template definitions in text format.
                - format ``str``: (optional) format of the template definitions. Defaults to sOTTR. Supported formats: sOTTR.

        """
        for template in parse_templates(text, format=format):
            self._templates[template.name] = template

    def instanciate(self, text, format="stottr"):
        """
            Instance a set of OTTR instances.
            Arguments:
                - text ``str``: OTTR instances in text format.
                - format ``str``: (optional) format of the template definitions. Defaults to sOTTR. Supported formats: sOTTR.

            Returns:
                A :class`ottr.generator.OttrInstances`
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

class OttrInstances(object):
    """Compiled OTTR instances, ready to be executed to produce RDF triples."""

    def __init__(self, id, to_execute, all_templates):
        super(OttrInstances, self).__init__()
        self._id = id
        self._to_execute = to_execute
        self._all_templates = all_templates

    def execute(self, as_nt=False):
        """
            Execute the instances to produce RDF triples.

            Arguments:
                - as_nt ``bool``: (optional) True if the results should be produced in text RDF format, False if they should be produced in RDFlib format.

            Returns:
                A generator that yields 3-tuples of ``str`` or :class`rdflib.term.Identifier` (depends on the value set for as_nt).
        """
        for template, params in self._to_execute:
            yield from template.expand(params, self._all_templates, bnode_suffix=(self._id, 0), as_nt=as_nt)
