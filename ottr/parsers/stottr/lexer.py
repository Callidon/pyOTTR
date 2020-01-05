# lexer.py
# Author: Thomas MINIER - MIT License 2019
import re
from pyparsing import CaselessKeyword, Keyword, LineEnd, Literal, MatchFirst, OneOrMore, Optional, Group, Regex, ZeroOrMore


def ListOf(content: Group, start_char: str = "(", end_char: str = ")", separator: str = ",") -> Group:
    """Build a group that matches a list of the same tokens.

    Args:
      * content: A Group of tokens.
      * start_char: Character at the start of the the list.
      * end_char: Character at the end of the the list.
      * separator: Character used to sperate elements in the list
    """
    # list_content = MatchFirst([
    #     content,
    #     content + Optional(Literal(separator)).suppress()
    # ])
    return Group(Literal(start_char).suppress() + OneOrMore(content + Optional(Literal(separator)).suppress()) + Literal(end_char).suppress())

# ----- General terms ------


uriref = r'(<([^:]+:[^\s"<>]+)>|(([A-Za-z0-9]|-)+):([A-Za-z0-9]+))'
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
r_prefix = re.compile(r'([A-Za-z0-9]|-)+')

# a suppressed comma (',')
comma = Literal(',').suppress()

# A Turtle Prefix
prefixName = Regex(r_prefix)

# The special 'none' keyword (a shorthand notation for ottr:None)
ottrNone = Keyword('none')

# a RDF IRI
iri = Regex(r_uriref)

# a RDF Blank Node
bnode = Regex(r_nodeid)

# a SPARQL variable
variable = Regex(r_variable)

# a RDF Literal
literal = Regex(r_literal)

# An IRI or a Variable
iriOrVariable = MatchFirst([iri, variable])

# Any valid RDF terms
anyTerm = MatchFirst([ottrNone, iri, literal, bnode, variable])

# Any valid concrete RDF terms, i.e., excluding SPARQL variables
concreteTerm = MatchFirst([ottrNone, iri, literal, bnode])

# ----- stOTTR language rules ------

# The List<T> type, where T is a type IRI
listType = Literal("List<").suppress() + iri + Literal(">").suppress()

# The type of a parameter
paramType = MatchFirst([
    listType.setResultsName('listType'),
    iri.setResultsName('type')
])

# The value of an argument
argumentValue = MatchFirst([
    anyTerm,
    ListOf(anyTerm),
    Group(Literal("++").suppress() + anyTerm)
])

# The value of a concrete argument, i.e., without any variables
concreteArgument = MatchFirst([
    concreteTerm,
    ListOf(concreteTerm)
])

# A template parameter definition, with optional type and nonblank
# Examples: "?iri", "xsd:string ?literal", "! otrr:IRI ?iri" or "?iri = ex:Ann"
param = Group(
    Optional(Keyword('!')).setResultsName('nonblank') +
    Optional(Keyword('?')).setResultsName('optional') +
    Optional(paramType) +
    variable.setResultsName('value') +
    Optional(Keyword('=') + concreteTerm.setResultsName('default'))
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
    OneOrMore(argumentValue + Optional(comma).suppress()).setResultsName('arguments') +
    Literal(')').suppress()
)

# An expansion of an instance
# example : cross | ottr:Triple(?s, ?p, ++?o)
expansionMode = Group(
    Keyword("cross").setResultsName('type') +
    Keyword("|").suppress() +
    instanceWithVars.setResultsName('content')
)

# A concrete instance of a template (which cannot contains variables)
# like ex:MyTemplate (ex:Ann, foaf:Person, "Ann Strong")
concreteInstance = Group(
    iri.setResultsName('name') +
    Literal('(').suppress() +
    OneOrMore(concreteArgument + Optional(comma).suppress()).setResultsName('arguments') +
    Literal(')').suppress()
)

# A stOTTR prefix declaration
prefixDeclaration = Group(
    CaselessKeyword("@prefix").suppress() +
    prefixName.setResultsName('name') +
    Literal(':').suppress() +
    iri.setResultsName('value') +
    Literal('.').suppress()
)

# A stOTTR template
ottrTemplate = Group(
    iri.setResultsName('name') +
    paramList.setResultsName('parameters') +
    Literal('::').suppress() +
    Literal('{').suppress() +
    ZeroOrMore(
        MatchFirst([instanceWithVars, expansionMode]) +
        Optional(',').suppress()
    ).setResultsName('instances') +
    Literal('}').suppress() + Literal('.').suppress()
)

# Several stOTTR templates
ottrRoot = ZeroOrMore(prefixDeclaration + LineEnd().suppress()).setResultsName('prefixes') + OneOrMore(ottrTemplate + LineEnd().suppress()).setResultsName('templates')

# Several concrete stOTTR instances (with no variables allowed)
ottrRootInstances = ZeroOrMore(prefixDeclaration + LineEnd().suppress()).setResultsName('prefixes') + OneOrMore(concreteInstance + Keyword('.').suppress() + Optional(LineEnd()).suppress()).setResultsName('instances')


def lex_templates_stottr(text: str) -> Group:
    """Run the lexer on a set of stOTTR template defintions.

    Argument: A set of stOTTR template defintions as text.

    Returns: The lexed stOTTR template defintions.
    """
    return ottrRoot.parseString(text)


def lex_instances_stottr(text: str) -> Group:
    """Run the lexer on a set of stOTTR instances.

    Argument: A set of stOTTR instances as text.

    Returns: The lexed stOTTR instances.
    """
    return ottrRootInstances.parseString(text)
