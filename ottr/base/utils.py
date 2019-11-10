# utils.py
# Author: Thomas MINIER - MIT License 2019
from rdflib.namespace import Namespace

# OTTR namespace
OTTR = Namespace('http://ns.ottr.xyz/0.4/')
OTTR_RDF = Namespace('http://tpl.ottr.xyz/rdf/0.1/')
OTTR_RDFS = Namespace('http://tpl.ottr.xyz/rdfs/0.1/')

# URI for OTTR base templates
OTTR_TRIPLE_URI = OTTR.Triple
OTTR_TYPE_URI = OTTR_RDF.Type
OTTR_LABEL_URI = OTTR_RDFS.Label
