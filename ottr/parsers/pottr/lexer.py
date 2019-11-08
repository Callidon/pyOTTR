# lexer.py
# Author: Thomas MINIER - MIT License 2019
import re
from pyparsing import CaselessKeyword, Keyword, LineEnd, Literal, MatchFirst, OneOrMore, Optional, Group, Regex, Word, ZeroOrMore

# ----- General terms ------

uriref = r'<([^:]+:[^\s"<>]+)>'
literal = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
litinfo = r'(?:@([a-zA-Z]+(?:-[a-zA-Z0-9]+)*)|\^\^' + uriref + r')?'

r_line = re.compile(r'([^\r\n]*)(?:\r\n|\r|\n)')
r_wspace = re.compile(r'[ \t]*')
r_wspaces = re.compile(r'[ \t]+')
r_tail = re.compile(r'[ \t]*\.[ \t]*(#.*)?')
r_uriref = re.compile(uriref)
r_uriprefix = re.compile(r'([A-Za-z0-9]+):([A-Za-z0-9]+)')
r_nodeid = re.compile(r'_:([A-Za-z0-9]*)')
r_literal = re.compile(literal + litinfo)
r_variable = re.compile(r'\?([A-Za-z0-9]+)')
r_prefix = re.compile(r'[A-Za-z0-9]+')

# a suppressed comma (',')
comma = Literal(',').suppress()

# a RDF IRI
iri = MatchFirst([Regex(r_uriref), Regex(r_uriprefix)])

# a RDF Blank Node
bnode = Regex(r_nodeid)

# a SPARQL variable
variable = Regex(r_variable)

# a RDF Literal
literal = Regex(r_literal)

# An IRI or a Variable
iriOrVariable = MatchFirst([iri, variable])

# Any valid RDF terms
rdfTerm = MatchFirst([iri, literal, bnode, variable])

# Any valid RDF terms, excluding SPARQL variables
rdfTermNoVars = MatchFirst([iri, literal, bnode, variable])

# A Turtle Prefix
prefixName = Regex(r_prefix)

# ----- OTTR macros ------

# A template parameter definition, with optional type and nonblank
# For example: ?iri or xsd:string ?literal or ! otrr:IRI ?iri
param = Group(
            Optional(Keyword('!')).setResultsName('nonblank') +
            Optional(Keyword('?')).setResultsName('optional') +
            Optional(iri).setResultsName('type') +
            variable.setResultsName('value')
        ).setResultsName('parameter') + Optional(',').suppress()

# A list of template parameters
paramList = Group(
                Literal('[').suppress() +
                ZeroOrMore(param) +
                Literal(']').suppress()
            )

# An instance of a template which may contains variables
# like ottr:Triple (_:person, rdf:type, ?person)
instanceWithVars = Group(
                    iri.setResultsName('name') +
                    Literal('(').suppress() +
                    OneOrMore(rdfTerm + Optional(comma).suppress()).setResultsName('parameters') +
                    Literal(')').suppress()
                )
# An instance of a template which cannot contains variables
# like ottr:Triple (_:person, rdf:type, ?person)
instanceNoVars = Group(
                    iri.setResultsName('name') +
                    Literal('(').suppress() +
                    OneOrMore(rdfTermNoVars + Optional(comma).suppress()).setResultsName('parameters') +
                    Literal(')').suppress()
                )

# An OTTR prefix declaration
prefixDeclaration = Group(
                CaselessKeyword("@prefix").suppress() +
                prefixName.setResultsName('name') +
                Literal(':').suppress() +
                iri.setResultsName('value') +
                Literal('.').suppress()
            )

# An OTTR template
ottrTemplate = Group(
                iri.setResultsName('name') +
                paramList.setResultsName('parameters') +
                Literal('::').suppress() +
                Literal('{').suppress() +
                ZeroOrMore(instanceWithVars + Optional(',').suppress()).setResultsName('instances') +
                Literal('}').suppress() + Literal('.').suppress()
            )

# Several OTTR templates
ottrRoot = ZeroOrMore(prefixDeclaration + LineEnd().suppress()).setResultsName('prefixes') + OneOrMore(ottrTemplate + LineEnd().suppress()).setResultsName('templates')

# Several concrete OTTR instances (with no variables allowed)
ottrRootInstances = ZeroOrMore(prefixDeclaration + LineEnd().suppress()).setResultsName('prefixes') + OneOrMore(instanceNoVars + Keyword('.').suppress() + Optional(LineEnd()).suppress()).setResultsName('instances')


def lex_templates_pottr(text):
    """Run the lexer on a set of pOTTR template defintions"""
    return ottrRoot.parseString(text)

def lex_instances_pottr(text):
    """Run the lexer on a set of pOTTR instances"""
    return ottrRootInstances.parseString(text)
