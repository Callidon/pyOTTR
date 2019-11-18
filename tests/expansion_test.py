# expansion_test.py
# Author: Thomas MINIER - MIT License 2019
import pytest
from ottr import OttrGenerator
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import FOAF, RDF

fixtures = [
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ List<ottr:IRI> ?emails ] :: {
            cross | ottr:Triple (_:person, foaf:mbox, ++?emails )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person( (<mailto:ann.strong@gmail.com>, <mailto:ann.strong@hotmail.fr>) ).
    """, [
        (BNode("person_0_0"), FOAF.mbox, URIRef("mailto:ann.strong@gmail.com")),
        (BNode("person_0_0"), FOAF.mbox, URIRef("mailto:ann.strong@hotmail.fr"))
    ])
]

@pytest.mark.parametrize("template,instance,expected", fixtures)
def test_expansion_modes(template, instance, expected):
    gen = OttrGenerator(load_defaults=False)
    gen.load_templates(template)
    instances = gen.instanciate(instance)
    for triple in instances.execute(as_nt=False):
        assert triple in expected
        # remove triple from the list of expected values
        expected.remove(triple)
    assert len(expected) == 0
