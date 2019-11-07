# parser.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers.pottr.lexer import lex_template_pottr
from rdflib import Graph, URIRef, Variable, BNode
from rdflib.namespace import RDFS
from rdflib.namespace import NamespaceManager
from rdflib.util import from_n3

def parse_term(term, nsm=None):
    """Parse a RDF Term from text format to rdflib format"""
    # rdflib tends to see SPARQL variables as blank nodes, so we need to handle them separately
    if term.startswith('?'):
        return Variable(term[1:])
    return from_n3(term, nsm=nsm)

def parse_template_parameter(param, position, nsm=None):
    """Parse an OTTR template parameter"""
    template_param = dict()
    template_param['name'] = parse_term(param.value, nsm=nsm)
    template_param['position'] = position
    template_param['type'] = param.type if len(param.type) > 0 else RDFS.Resource
    template_param['optional'] = True if len(param.optional) > 0 else False
    template_param['nonblank'] = True if len(param.nonblank) > 0 else False
    return template_param

def parse_template_instance(instance, nsm=None):
    """Parse an OTTR template instance"""
    template_instance = dict()
    template_instance['name'] = parse_term(instance.name, nsm=nsm)
    # parse instance parameters
    instance_params = list()
    for i in range(len(instance.parameters.asList())):
        current_param = dict()
        current_param['position'] = i
        current_param['value'] = parse_term(instance.parameters[i], nsm=nsm)
        # save parameter
        instance_params.append(current_param)
    template_instance['parameters'] = instance_params
    return template_instance

def parse_template_pottr(text):
    """Parse a set of pOTTR template definitions and returns the list of all OTTR templates."""
    # create a RDFLib NamespaceManager to handle automatic prefix expansion
    nsm = NamespaceManager(Graph())
    # add some prefixes commonly used in pOTTR documents
    nsm.bind('ottr', 'http://ns.ottr.xyz/0.4/')
    nsm.bind('foaf', 'http://xmlns.com/foaf/0.1/')
    nsm.bind('dc', 'http://purl.org/dc/elements/1.1/')
    nsm.bind('owl', 'http://www.w3.org/2002/07/owl#')
    nsm.bind('ax', 'http://tpl.ottr.xyz/owl/axiom/0.1/')
    nsm.bind('rstr', 'http://tpl.ottr.xyz/owl/restriction/0.1/')
    nsm.bind('schema', 'http://schema.org/')
    nsm.bind('schemas', 'https://schema.org/')

    # run pOTTR lexer
    tree = lex_template_pottr(text)

    # parse prefixes and register them into the NamespaceManager
    for prefix in tree.prefixes:
        uri = prefix.value
        if uri.startswith('<') and uri.endswith('>'):
            uri = uri[1: -1]
        nsm.bind(prefix.name, uri, replace=True)

    # parse each template definition found
    ottr_templates = list()
    for template in tree.templates:
        ottr_template = dict()
        # create template name
        ottr_template['name'] = parse_term(template.name, nsm=nsm)

        # parse parameters
        template_params = list()
        for pos in range(len(template.parameters.asList())):
            template_params.append(parse_template_parameter(template.parameters[pos], pos, nsm=nsm))
        ottr_template['parameters'] = template_params

        # parse instances
        template_instances = list()
        for instance in template.instances:
            template_instances.append(parse_template_instance(instance, nsm=nsm))
        ottr_template['instances'] = template_instances

        # register the new OTTR template
        ottr_templates.append(ottr_template)
    return ottr_templates


# ---- Testing -----
if __name__ == "__main__":

    parsed = parse_template_pottr("""
        @prefix ex: <http://example.org#>.
        ex:Person[ ?firstName, ?lastName, ?email ] :: {
            ottr:Triple (_:person, rdf:type, foaf:Person),
            ottr:Triple (_:person, foaf:firstName, ?firstName)
        } .
    """)

    print(parsed)
