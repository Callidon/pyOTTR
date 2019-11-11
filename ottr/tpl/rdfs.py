# rdfs.py
# Author: Thomas MINIER - MIT License 2019

RDFS_TEMPLATES = """
@prefix o-rdfs: <http://tpl.ottr.xyz/rdfs/0.1/> .

o-rdfs:Label[ ottr:IRI ?iri, ?label ] :: {
    ottr:Triple(?iri, rdfs:label, ?label)
} .

o-rdfs:ResourceDescription[ ottr:IRI ?iri, ? ?label, ? ?comment, ? ?seeAlso, ? ?isDefinedBy ] :: {
    o-rdfs:Label(?iri, ?label),
    ottr:Triple(?iri, rdfs:comment, ?comment),
    ottr:Triple(?iri, rdfs:seeAlso, ?seeAlso),
    ottr:Triple(?iri, rdfs:isDefinedBy, ?isDefinedBy)
} .

o-rdfs:TypedResourceDescription[ ottr:IRI ?iri, ottr:IRI ?type, ? ?label, ? ?comment, ? ?seeAlso, ? ?isDefinedBy ] :: {
    ottr:Triple(?iri, rdf:type, ?type),
    o-rdfs:ResourceDescription(?iri, ?label, ?comment, ?seeAlso, ?isDefinedBy)    
} .
"""
