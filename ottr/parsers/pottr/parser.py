# parser.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers.pottr.lexer import lex_template_pottr
from ottr.base.base_templates import OttrTriple
from ottr.base.template import MainTemplate
from ottr.base.parameter import ConcreteParameter, VariableParameter
from ottr.base.utils import OTTR_TRIPLE_URI
from rdflib import Graph, Variable
from rdflib.namespace import RDFS
from rdflib.namespace import NamespaceManager
from rdflib.util import from_n3

def parse_term(term, nsm=None):
    """Parse a RDF Term from text format to rdflib format"""
    # rdflib tends to see SPARQL variables as blank nodes, so we need to handle them separately
    if term.startswith('?'):
        return Variable(term[1:])
    return from_n3(term, nsm=nsm)

def parse_template_parameter(param, nsm=None):
    """Parse an OTTR template parameter"""
    template_param = dict()
    template_param['name'] = parse_term(param.value, nsm=nsm)
    template_param['type'] = param.type if len(param.type) > 0 else RDFS.Resource
    template_param['optional'] = True if len(param.optional) > 0 else False
    template_param['nonblank'] = True if len(param.nonblank) > 0 else False
    return template_param

def parse_template_instance(instance, nsm=None):
    """Parse an OTTR template instance"""
    template_name = parse_term(instance.name, nsm=nsm)

    # case 1: base template ottr:Triple
    if template_name == OTTR_TRIPLE_URI:
        # TODO check that the instance has only 3 parameters
        params = list()
        for parameter in instance.parameters:
            value = parse_term(parameter, nsm=nsm)
            if type(value) is Variable:
                params.append(VariableParameter(value))
            else:
                params.append(ConcreteParameter(value))
        return OttrTriple(params[0], params[1], params[2])

    # case 2: base template ottr:NullableTriple
    # TODO

    # case 2: a non-base template instance
    # TODO store the template def. for now, and then inline it until
    # there is only base template instance inside the template definition
    # This will greatly simplify processing and boost perfs, as we will avoid large recursions
    return None

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
        # ottr_template = dict()
        template_name = parse_term(template.name, nsm=nsm)

        # parse parameters
        template_params = list()
        for pos in range(len(template.parameters.asList())):
            parameter = parse_template_parameter(template.parameters[pos], nsm=nsm)
            # TODO handle parameter better than that
            template_params.append((parameter['name'], pos))

        # parse instances
        template_instances = list()
        for instance in template.instances:
            template_instances.append(parse_template_instance(instance, nsm=nsm))

        # create the OTTR template & register its parameters
        ottr_template = MainTemplate(template_name, template_instances)
        for name, position in template_params:
            ottr_template.add_parameter(name, position)
        # register the new OTTR template
        ottr_templates.append(ottr_template)
    return ottr_templates
