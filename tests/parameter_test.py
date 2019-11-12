# stootr_test.py
# Author: Thomas MINIER - MIT License 2019
import pytest
from ottr import OttrGenerator
from rdflib import BNode, Literal, URIRef
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
    """, "Invalid argument \"ex:Ann\" used for parameter \"<http://ns.ottr.xyz/0.4/IRI> ?uri\". Reason : expected an IRI but instead got a <class 'rdflib.term.Literal'>"),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ xsd:integer ?age ] :: {
          ottr:Triple (_:person, foaf:age, ?age )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person("12"^^xsd:number).
    """, """Invalid argument "12"^^<http://www.w3.org/2001/XMLSchema#number> used for parameter "<http://www.w3.org/2001/XMLSchema#integer> ?age". Reason : expected a Literal with datatype <http://www.w3.org/2001/XMLSchema#integer> but instead got http://www.w3.org/2001/XMLSchema#number"""),
    # optional errors
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ?uri ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(ottr:None).
    """, """Invalid argument <http://ns.ottr.xyz/0.4/None> used for parameter "<http://www.w3.org/2000/01/rdf-schema#Resource> ?uri". Reason : this parameter is not optional, so it cannot be bound to ottr:none."""),
    # non blank errors
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ! ?uri ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(_:person).
    """, """Invalid argument _:person used for parameter "! <http://www.w3.org/2000/01/rdf-schema#Resource> ?uri". Reason : this parameter is non blank, so it cannot be bound to a blank node."""),
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
    """, [ (URIRef("http://example.org#Ann"), RDF.type, FOAF.Person) ]),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ottr:IRI ?uri, xsd:integer ?age ] :: {
          ottr:Triple (?uri, foaf:age, ?age )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(ex:Ann, "12"^^xsd:integer).
    """, [ (URIRef("http://example.org#Ann"), FOAF.age, Literal(12)) ]),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ! ?uri ] :: {
          o-rdf:Type (?uri, foaf:Person )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(ex:Ann).
    """, [ (URIRef("http://example.org#Ann"), RDF.type, FOAF.Person) ])
]

@pytest.mark.parametrize("template,instance,expected_err", failing_tests)
def test_invalid_parameter(template, instance, expected_err):
    gen = OttrGenerator()
    gen.load_templates(template)
    try:
        instances = gen.instanciate(instance)
    except Exception as e:
        assert str(e).strip() == expected_err

@pytest.mark.parametrize("template,instance,expected", correct_tests)
def test_valid_parameter(template, instance, expected):
    gen = OttrGenerator()
    gen.load_templates(template)
    instances = gen.instanciate(instance)
    for triple in instances.execute(as_nt=False):
        assert triple in expected
        expected.remove(triple)
    assert len(expected) == 0
