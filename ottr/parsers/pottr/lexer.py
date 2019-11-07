# lexer.py
# Author: Thomas MINIER - MIT License 2019
import re
from pyparsing import Regex, Group, Word, Optional, OneOrMore, ZeroOrMore, Literal, Or, LineEnd

# ----- General terms ------

uriref = r'<([^:]+:[^\s"<>]+)>'
literal = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
litinfo = r'(?:@([a-zA-Z]+(?:-[a-zA-Z0-9]+)*)|\^\^' + uriref + r')?'

r_line = re.compile(r'([^\r\n]*)(?:\r\n|\r|\n)')
r_wspace = re.compile(r'[ \t]*')
r_wspaces = re.compile(r'[ \t]+')
r_tail = re.compile(r'[ \t]*\.[ \t]*(#.*)?')
r_uriref = re.compile(uriref)
r_nodeid = re.compile(r'_:([A-Za-z0-9]*)')
r_literal = re.compile(literal + litinfo)
r_variable = re.compile(r'\?([A-Za-z0-9]+)')

# a suppressed comma (',')
comma = Literal(',').suppress()

# a RDF IRI
iri = Regex(r_uriref)

# a RDF Blank Node
bnode = Regex(r_nodeid)

# a SPARQL variable
variable = Regex(r_variable)

# a RDF Literal
literal = Regex(r_literal)

# An IRI or a Variable
iriOrVariable = Or([iri, variable])

# Any valid RDF terms
rdfTerm = Or([iri, literal, bnode, variable])

# ----- OTTR macros ------

# A template parameter definition, with optional type and nonblank
# For example: ?iri or xsd:string ?literal or ! otrr:IRI ?iri
param = Group(
            Optional(Literal('! ')).setResultsName('nonblank') +
            Optional(Literal('? ')).setResultsName('optional') +
            Optional(iri).setResultsName('type') +
            variable.setResultsName('value')
        ).setResultsName('parameter') + Optional(',').suppress()

# A list of template parameters
paramList = Group(
                Literal('[').suppress() +
                ZeroOrMore(param) +
                Literal(']').suppress()
            ).setResultsName('paramList')

# An instance of a template
# like ottr:Triple (_:person, rdf:type, foaf:Person)
instance = Group(
            iri.setResultsName('fnName') +
            Literal('(').suppress() +
            OneOrMore(rdfTerm + Optional(comma).suppress()).setResultsName('params') +
            Literal(')').suppress()
        )

# An OTTR prefix declaration
# ottrPrefix = Group(
#                 Literal("@prefix").suppress() +
#                 rdfWord.setResultsName('name') +
#                 Literal(':').suppress() +
#                 Literal('<').suppress() +
#                 iri.setResultsName('value') +
#                 Literal('>').suppress() +
#                 Literal('.').suppress()
#             )

# An OTTR template
ottrTemplate = Group(
                iri.setResultsName('templateName') +
                paramList.setResultsName('parameters') +
                Literal('::').suppress() +
                Literal('{').suppress() +
                ZeroOrMore(instance + Optional(',').suppress()).setResultsName('instances') +
                Literal('}').suppress() + Literal('.').suppress()
            )

# Several OTTR templates
ottrRoot = OneOrMore(ottrTemplate + LineEnd().suppress()).setResultsName('templates')


def lex_template_pottr(text):
    """Run the lexer on a pOTTR template file"""
    return ottrRoot.parseString(text)
