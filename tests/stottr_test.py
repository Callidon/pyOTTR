# stootr_test.py
# Author: Thomas MINIER - MIT License 2019
import pytest
from ottr import OttrGenerator
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import FOAF, RDF

fixtures = [
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ?firstName, ?lastName, ?email ] :: {
            o-rdf:Type (_:person, foaf:Person ),
            ottr:Triple (_:person, foaf:firstName, ?firstName ),
            ottr:Triple (_:person, foaf:lastName, ?lastName ),
            ottr:Triple (_:person, foaf:mbox, ?email )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person("Ann", "Strong", <mailto:ann.strong@gmail.com>).
    """, [
        (BNode("person_0_1"), RDF.type, FOAF.Person),
        (BNode("person_0_0"), FOAF.firstName, Literal("Ann")),
        (BNode("person_0_0"), FOAF.lastName, Literal("Strong")),
        (BNode("person_0_0"), FOAF.mbox, URIRef("mailto:ann.strong@gmail.com"))
    ]),
    ("""
        @prefix ex: <http://example.org#>.
        ex:FirstName [?uri, ?firstName] :: {
            ottr:Triple (?uri, foaf:firstName, ?firstName )
        } .
        ex:Person[ ?firstName ] :: {
          o-rdf:Type (_:person, foaf:Person ),
          ex:FirstName (_:person, ?firstName)
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person("Ann").
    """, [
        (BNode("person_0_1"), RDF.type, FOAF.Person),
        (BNode("person_0_1"), FOAF.firstName, Literal("Ann"))
    ])
]


@pytest.mark.parametrize("template,instance,expected", fixtures)
def test_triple_generation(template, instance, expected):
    gen = OttrGenerator()
    gen.load_templates(template)
    instances = gen.instanciate(instance)
    for triple in instances.execute(as_nt=False):
        assert triple in expected
        # remove triple from the list of expected values
        expected.remove(triple)
    assert len(expected) == 0
