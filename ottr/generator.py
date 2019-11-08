# generator.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers import parse_templates, parse_instances
from rdflib import URIRef, Variable, Literal

class OttrGenerator(object):
    """
        An OttrGenerator can load OTTR templates definitions and expand them to produce RDF triples.
    """

    def __init__(self):
        super(OttrGenerator, self).__init__()
        self._templates = dict()

    def loadTemplates(self, text, format="stottr"):
        """Load a set of pOTTR template definitions"""
        for template in parse_templates(text, format=format):
            self._templates[template.name] = template

    def instanciate(self, text, format="stottr"):
        # parse instances
        instances = parse_instances(text, format=format)
        # create pairs of (instance, related template)
        to_execute = list()
        for instance in instances:
            if instance['name'] in self._templates:
                template = self._templates[instance['name']]
                exec_parameters = template.format_parameters(instance['parameters'])
                to_execute.append((template, exec_parameters))
            else:
                # TODO report error but do not crash??
                pass
        return OttrInstances(to_execute)

class OttrInstances(object):
    """Compiled OTTR instances, ready to be executed to produce RDF triples."""

    def __init__(self, to_execute):
        super(OttrInstances, self).__init__()
        self._to_execute = to_execute

    def execute(self, as_nt=False):
        for template, params in self._to_execute:
            yield from template.expand(params, as_nt=as_nt)


# ---- Testing -----
if __name__ == '__main__':
    gen = OttrGenerator()
    gen.loadTemplates("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ?firstName, ?lastName, ?email ] :: {
          ottr:Triple (_:person, rdf:type, foaf:Person ),
          ottr:Triple (_:person, foaf:firstName, ?firstName ),
          ottr:Triple (_:person, foaf:lastName, ?lastName ),
          ottr:Triple (_:person, foaf:mbox, ?email )
        } .
    """)
    instances = gen.instanciate("""
        @prefix ex: <http://example.org#>.
        ex:Person("Ann", "Strong", <mailto:ann.strong@gmail.com>).
    """)
    for triple in instances.execute(as_nt=True):
        print(triple)
