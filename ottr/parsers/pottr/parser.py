# parser.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers.pottr.lexer import lex_template_pottr
from rdflib import URIRef, Variable, BNode
import rdflib.namespace as PREFIXES


def parse_term(text):
    """Parse a RDF Term into RDFlib format"""
    term = text
    if term.startswith('<') and term.endswith('>'):
        return URIRef(term[1:-1])
    if term.startswith('?'):
        return Variable(term[1:])
    if term.startswith('_:'):
        return BNode(term[2:])
    # TODO handle literals
    return None

def parse_template_parameter(param, position):
    """Parse an OTTR template parameter"""
    template_param = dict()
    template_param['name'] = Variable(param.value)
    template_param['position'] = position
    template_param['type'] = param.type if len(param.type) > 0 else PREFIXES.RDFS.Resource
    template_param['optional'] = True if len(param.optional) > 0 else False
    template_param['nonblank'] = True if len(param.nonblank) > 0 else False
    return template_param

def parse_template_instance(instance):
    """Parse an OTTR template instance"""
    template_instance = dict()
    template_instance['name'] = parse_term(instance.name)
    # parse instance parameters
    instance_params = list()
    for i in range(len(instance.parameters.asList())):
        current_param = dict()
        current_param['position'] = i
        current_param['value'] = parse_term(instance.parameters[i])
        # save parameter
        instance_params.append(current_param)
    template_instance['parameters'] = instance_params
    return template_instance

def parse_template_pottr(text):
    """Parse a set of pOTTR template definitions and returns the list of all OTTR templates."""
    tree = lex_template_pottr(text)
    # parse each template found
    ottr_templates = list()
    for template in tree.templates:
        ottr_template = dict()
        # create template name
        # TODO: only works for full IRI, not prefixed IRIs
        ottr_template['name'] = parse_term(template.name)

        # parse parameters
        template_params = list()
        for pos in range(len(template.parameters.asList())):
            template_params.append(parse_template_parameter(template.parameters[pos], pos))
        ottr_template['parameters'] = template_params

        # parse instances
        template_instances = list()
        for instance in template.instances:
            template_instances.append(parse_template_instance(instance))
        ottr_template['instances'] = template_instances

        # register the new OTTR template
        ottr_templates.append(ottr_template)
    return ottr_templates


# ---- Testing -----
if __name__ == "__main__":

    parsed = parse_template_pottr("""
        <http://example.org#Person>[ ?firstName, ?lastName, ?email ] :: {
            <http://ottr.xyz#Triple> (_:person, <http://rdf.com#type>, <http://foaf.com#Person>),
            <http://ottr.xyz#Triple> (_:person, <http://foaf.com#firstName>, ?firstName)
        } .
    """)

    print(parsed)
