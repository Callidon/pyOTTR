# parser.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers.pottr.lexer import lex_template_pottr
from rdflib import URIRef, Variable
import rdflib.namespace as PREFIXES


def parse_template_parameter(param):
    """Parse an OTTR template parameter"""
    template_param = dict()
    template_param['name'] = Variable(param.value)
    template_param['type'] = param.type if len(param.type) > 0 else PREFIXES.RDFS.Resource
    template_param['optional'] = True if param.optional == '?' else False
    template_param['nonblank'] = True if param.nonblank == '!' else False
    return template_param

def parse_template_pottr(text):
    """Parse a set of pOTTR template definitions and returns the list of all OTTR templates."""
    tree = lex_template_pottr(text)
    # parse each template found
    ottr_templates = list()
    for template in tree.templates:
        ottr_template = dict()
        # create template name
        # TODO: only works for full IRI, not prefixed IRIs
        template_name = template.templateName
        if template_name.startswith('<') and template_name.endswith('>'):
            template_name = template_name[1:-1]
        ottr_template['name'] = URIRef(template_name)

        # parse parameters
        template_params = list()
        for param in template.parameters:
            template_params.append(parse_template_parameter(param))
        ottr_template['parameters'] = template_params

        # parse instances
        template_instances = list()
        # TODO
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
