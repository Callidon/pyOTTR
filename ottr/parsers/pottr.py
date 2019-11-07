# pottr.py
# Author: Thomas MINIER - MIT License 2019
from pyparsing import Group, Word, alphas, Optional, OneOrMore, ZeroOrMore, White, Literal, srange, Or, LineEnd

# ----- General terms ------

# A word, as allowed by the RDF syntax
rdfWord = Word(srange("[a-zA-Z_]"), excludeChars="@")

# a suppressed comma (',')
comma = Literal(',').suppress()

# a RDF IRI
iri = Group(rdfWord.setResultsName('prefix') + Literal(":").suppress() + rdfWord.setResultsName('suffix'))

# a SPARQL variable
variable = Word('?' + srange("[a-zA-Z_]"))

# a RDF Literal
literal = Or(['"' + rdfWord + '"', '"' + rdfWord + '"^^' + iri, '"' + rdfWord + '"@' + rdfWord])

# An IRI or a Variable
iriOrVariable = Or([iri, variable])

# Any valid RDF terms
anyTerm = Or([iri, literal, variable])

# ----- OTTR macros ------

# A template parameter definition, with optional type and nonblank
# For example: ?iri or xsd:string ?literal or ! otrr:IRI ?iri
param = Group(
            Optional(Literal('!')).setResultsName('nonblank') +
            Optional(Literal('?')).setResultsName('optional') +
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
            OneOrMore(anyTerm + Optional(comma).suppress()).setResultsName('params') +
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

# ---- Testing -----

text = """
    ex:Person[ ?firstName, ?lastName, ?email ] :: {
      ottr:Triple (_:person, rdf:type, foaf:Person),
      ottr:Triple (_:person, foaf:firstName, ?firstName )
    } .
"""

tree = ottrRoot.parseString(text)

print('found ' + str(len(tree.templates.asList())) + ' template definition(s)')

for temp in tree:
    print("# ----------------- #")
    print('Template name: {}'.format(temp.templateName.asList()))
    print('nb parameters: {}'.format(len(temp.parameters)))
    print('parameters: {}'.format(temp.parameters.asList()))
    print('nb instances: {}'.format(len(temp.instances)))

    for instance in temp.instances:
        print('-----------------')
        print('Instance name: {}'.format(instance.fnName.asList()))
        print('nb parameters: {}'.format(len(instance.params.asList())))
        print('parameters: {}'.format(instance.params.asList()))
print("# ----------------- #")
