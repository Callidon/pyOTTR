# parser.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers.pottr.lexer import lex_template_pottr
from rdflib import Graph, URIRef, Variable, BNode
from rdflib.namespace import RDFS
from rdflib.namespace import NamespaceManager
from rdflib.util import from_n3

def parse_template_parameter(param, position, nsm=None):
    """Parse an OTTR template parameter"""
    template_param = dict()
    template_param['name'] = from_n3(param.value, nsm=nsm)
    template_param['position'] = position
    template_param['type'] = param.type if len(param.type) > 0 else RDFS.Resource
    template_param['optional'] = True if len(param.optional) > 0 else False
    template_param['nonblank'] = True if len(param.nonblank) > 0 else False
    return template_param

def parse_template_instance(instance, nsm=None):
    """Parse an OTTR template instance"""
    template_instance = dict()
    template_instance['name'] = from_n3(instance.name, nsm=nsm)
    # parse instance parameters
    instance_params = list()
    for i in range(len(instance.parameters.asList())):
        current_param = dict()
        current_param['position'] = i
        current_param['value'] = from_n3(instance.parameters[i], nsm=nsm)
        # save parameter
        instance_params.append(current_param)
    template_instance['parameters'] = instance_params
    return template_instance

def parse_template_pottr(text):
    """Parse a set of pOTTR template definitions and returns the list of all OTTR templates."""
    # create a RDFLib NamespaceManager to handle automatic prefix expansion
    nsm = NamespaceManager(Graph())
    # add some common prefixes used in pOTTR documents
    nsm.bind('ottr', 'http://ns.ottr.xyz/0.4/')
    nsm.bind('foaf', 'http://xmlns.com/foaf/0.1/')
    nsm.bind('owl', 'http://www.w3.org/2002/07/owl#')
    nsm.bind('ax', 'http://tpl.ottr.xyz/owl/axiom/0.1/')
    nsm.bind('rstr', 'http://tpl.ottr.xyz/owl/restriction/0.1/')

    # run pOTTR lexer
    tree = lex_template_pottr(text)

    # parse each template found by the lexer
    ottr_templates = list()
    for template in tree.templates:
        ottr_template = dict()
        # create template name
        # TODO: only works for full IRI, not prefixed IRIs
        ottr_template['name'] = from_n3(template.name, nsm=nsm)

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
        ottr:Person[ ?firstName, ?lastName, ?email ] :: {
            ottr:Triple (_:person, rdf:type, foaf:Person),
            ottr:Triple (_:person, foaf:firstName, ?firstName)
        } .
    """)

    print(parsed)
