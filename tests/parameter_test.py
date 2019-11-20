# stootr_test.py
# Author: Thomas MINIER - MIT License 2019
import pytest
from ottr import OttrGenerator
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, FOAF

failing_tests = [
    # type related errors
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ottr:IRI ?uri ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person("ex:Ann").
    """),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ xsd:integer ?age ] :: {
          ottr:Triple (_:person, foaf:age, ?age )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person("12"^^xsd:number).
    """),
    # optional errors
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ?uri ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(none).
    """),
    # non blank errors
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ! ?uri ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(_:person).
    """),
]

correct_tests = [
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ottr:IRI ?uri ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person (ex:Ann).
    """, [(URIRef("http://example.org#Ann"), RDF.type, FOAF.Person)]),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ottr:IRI ?uri, xsd:integer ?age ] :: {
          ottr:Triple (?uri, foaf:age, ?age )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(ex:Ann, "12"^^xsd:integer).
    """, [(URIRef("http://example.org#Ann"), FOAF.age, Literal(12))]),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ! ?uri ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(ex:Ann).
    """, [(URIRef("http://example.org#Ann"), RDF.type, FOAF.Person)]),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ?uri = ex:Ann ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(none).
    """, [(URIRef("http://example.org#Ann"), RDF.type, FOAF.Person)])
]


@pytest.mark.parametrize("template,instance", failing_tests)
def test_invalid_parameter(template, instance):
    gen = OttrGenerator()
    gen.load_templates(template)
    with pytest.raises(Exception):
        gen.instanciate(instance)


@pytest.mark.parametrize("template,instance,expected", correct_tests)
def test_valid_parameter(template, instance, expected):
    gen = OttrGenerator()
    gen.load_templates(template)
    instances = gen.instanciate(instance)
    for triple in instances.execute(as_nt=False):
        assert triple in expected
        expected.remove(triple)
    assert len(expected) == 0
