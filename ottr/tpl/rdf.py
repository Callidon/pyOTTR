# rdf.py
# Author: Thomas MINIER - MIT License 2019

RDF_TEMPLATES = """
@prefix o-rdf: <http://tpl.ottr.xyz/rdf/0.1/> .

o-rdf:Type[ ottr:IRI ?entity, ottr:IRI ?type ] :: {
    ottr:Triple(?entity, rdf:type, ?type)
} .
"""
