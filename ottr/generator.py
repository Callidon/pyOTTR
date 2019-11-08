# generator.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers import parse_templates
from rdflib import URIRef, Variable, Literal

class OttrGenerator(object):
    """docstring for OttrGenerator."""

    def __init__(self):
        super(OttrGenerator, self).__init__()
        self._templates = dict()

    def loadTemplates(self, text, format="pottr"):
        """Load a set of pOTTR template definitions"""
        for template in parse_templates(text, format=format):
            self._templates[template.name] = template

    def instanciate(self, format="pottr"):
        template = self._templates[URIRef('http://example.org#Person')]
        return OttrInstances([template])

class OttrInstances(object):
    """docstring for OttrInstances."""

    def __init__(self, instances):
        super(OttrInstances, self).__init__()
        self._instances = instances

    def execute(self, as_nt=False):
        for template in self._instances:
            instance_params = template.format_parameters([(0, Literal('Ann')), (1, Literal('Strong')), (2, URIRef('mailto:ann.strong@gmail.com'))])
            yield from template.expand(instance_params, as_nt=as_nt)


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
    instances = gen.instanciate()
    for triple in instances.execute(as_nt=True):
        print(triple)
