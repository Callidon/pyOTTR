# expansion_test.py
# Author: Thomas MINIER - MIT License 2019
import pytest
from ottr import OttrGenerator
from rdflib import URIRef
from rdflib.namespace import FOAF

fixtures = [
    ("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ottr:IRI ?iri, List<ottr:IRI> ?emails ] :: {
            cross | ottr:Triple (?iri, foaf:mbox, ++?emails )
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person( ex:Ann, (<mailto:ann.strong@gmail.com>, <mailto:ann.strong@hotmail.fr>) ).
    """, [
        (URIRef("http://example.org#Ann"), FOAF.mbox, URIRef("mailto:ann.strong@gmail.com")),
        (URIRef("http://example.org#Ann"), FOAF.mbox, URIRef("mailto:ann.strong@hotmail.fr"))
    ]),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Emails [ ?iri, List<ottr:IRI> ?emails ] :: {
            cross | ottr:Triple (?iri, foaf:mbox, ++?emails )
        } .
        ex:Person[ ottr:IRI ?iri, List<ottr:IRI> ?emails ] :: {
            ex:Emails(?iri, ?emails)
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person( ex:Ann, (<mailto:ann.strong@gmail.com>, <mailto:ann.strong@hotmail.fr>) ).
    """, [
        (URIRef("http://example.org#Ann"), FOAF.mbox, URIRef("mailto:ann.strong@gmail.com")),
        (URIRef("http://example.org#Ann"), FOAF.mbox, URIRef("mailto:ann.strong@hotmail.fr"))
    ]),
    ("""
        @prefix ex: <http://example.org#>.
        ex:Emails [ ?iri, List<ottr:IRI> ?emails ] :: {
            cross | ottr:Triple (?iri, foaf:mbox, ++?emails )
        } .
        ex:Person[ ottr:IRI ?iri] :: {
            ex:Emails(?iri, (<mailto:ann.strong@gmail.com>, <mailto:ann.strong@hotmail.fr>))
        } .
    """, """
        @prefix ex: <http://example.org#>.
        ex:Person(ex:Ann).
    """, [
        (URIRef("http://example.org#Ann"), FOAF.mbox, URIRef("mailto:ann.strong@gmail.com")),
        (URIRef("http://example.org#Ann"), FOAF.mbox, URIRef("mailto:ann.strong@hotmail.fr"))
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
