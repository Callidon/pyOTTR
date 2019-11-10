# stootr_test.py
# Author: Thomas MINIER - MIT License 2019
from ottr import OttrGenerator
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import FOAF, RDF


def test_simple_generation():
    expected = [
        (BNode("person"), RDF.type, FOAF.Person),
        (BNode("person"), FOAF.firstName, Literal("Ann")),
        (BNode("person"), FOAF.lastName, Literal("Strong")),
        (BNode("person"), FOAF.mbox, URIRef("mailto:ann.strong@gmail.com"))
    ]
    gen = OttrGenerator()
    gen.loadTemplates("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ?firstName, ?lastName, ?email ] :: {
          o-rdf:Type (_:person, foaf:Person ),
          ottr:Triple (_:person, foaf:firstName, ?firstName ),
          ottr:Triple (_:person, foaf:lastName, ?lastName ),
          ottr:Triple (_:person, foaf:mbox, ?email )
        } .
    """)
    instances = gen.instanciate("""
        @prefix ex: <http://example.org#>.
        ex:Person("Ann", "Strong", <mailto:ann.strong@gmail.com>).
    """)
    for triple in instances.execute(as_nt=False):
        assert triple in expected
        # remove triple from the list of expected values
        expected.remove(triple)
    assert len(expected) == 0
