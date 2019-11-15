# parser.py
# Author: Thomas MINIER - MIT License 2019
from ottr.parsers.stottr.lexer import lex_templates_stottr, lex_instances_stottr
from ottr.base.base_templates import OttrTriple
from ottr.base.template import MainTemplate, NonBaseInstance
from ottr.base.argument import ConcreteArgument, VariableArgument
from ottr.base.utils import OTTR_TRIPLE_URI, OTTR_NONE
from rdflib import Graph, Variable
from rdflib.namespace import RDFS
from rdflib.namespace import NamespaceManager
from rdflib.util import from_n3

# All base templates are registered here,
# as tuples (template constructor, expected nb of arguments)
BASE_TEMPLATES = {
    OTTR_TRIPLE_URI: (OttrTriple, 3)
}

def unify_var(variable, suffix):
    """
        Makes a :class`rdflib.term.Variable` unique by appending a suffix to it.

        Arguments:
            - value :class`rdflib.term.Variable`: Variable to makes unique
            - suffix ``number|str``: suffix to hash & append at the end of the value
        Returns:
            A :class`rdflib.term.Variable`
    """
    return Variable("{}_{}".format(str(variable), suffix))

def get_default_nsm():
    """Get an rdflib NamespaceManager wirh default prefixes configured"""
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
    # OTTR base template library
    nsm.bind('o-rdf', 'http://tpl.ottr.xyz/rdf/0.1/')
    nsm.bind('o-rdfs', 'http://tpl.ottr.xyz/rdfs/0.1/')
    return nsm

def parse_term(term, nsm=None):
    """
        Parse a RDF Term from text format to rdflib format.

        Arguments:
            - term ``str``: RDF Term to parse (in text format)
            - nsm :class `rdflib.namespace.NamespaceManager`: (optional) RDFlib namespace manager used to manage prefixes.
    """
    # the special keyword "none" is interpreted as "ottr:None"
    if term == "none":
        return OTTR_NONE
    # rdflib tends to see SPARQL variables as blank nodes, so we need to handle them separately
    if term.startswith('?'):
        return Variable(term[1:])
    return from_n3(term, nsm=nsm)

def parse_instance_arguments(template_id, arguments, nsm=None):
    """
        Parse the arguments of a template instance.

        Arguments:
            - template_id ``int``: ID of the template
            - arguments ``str[]``: instance arguments to parse
            - nsm :class `rdflib.namespace.NamespaceManager`: (optional) RDFlib namespace manager used to manage prefixes.

        Retuns:
         A list of :class`ottr.base.InstanceArgument`
    """
    args = list()
    for ind in range(len(arguments)):
        argument = arguments[ind]
        value = parse_term(argument, nsm=nsm)
        # rewrite variables to make them unique for this scope
        if type(value) is Variable:
            value = unify_var(value, template_id)
            args.append(VariableArgument(value, ind))
        else:
            args.append(ConcreteArgument(value, ind))
    return args

def parse_template_parameter(template_id, param, nsm=None):
    """
        Parse an OTTR template parameter.

        Arguments:
            - template_id ``int``: ID of the template
            - param ``str[]``: parameter to parse
            - nsm :class`rdflib.namespace.NamespaceManager`: (optional) RDFlib namespace manager used to manage prefixes.

        Returns:
         A `dict` representation of the parsed template parameter, with fields "name" (:class`rdflib.term.Identifier`), "type" (:class`rdflib.term.URIRef`), "optional" (``bool``) and "nonblank" (``bool``).
    """
    template_param = dict()
    template_param['name'] = parse_term(param.value, nsm=nsm)
    # rewrite variables to make them unique for this scope
    if type(template_param['name']) == Variable:
        template_param['name'] = unify_var(template_param['name'], template_id)
    template_param['type'] = parse_term(param.type, nsm=nsm) if len(param.type) > 0 else RDFS.Resource
    template_param['optional'] = True if len(param.optional) > 0 else False
    template_param['nonblank'] = True if len(param.nonblank) > 0 else False
    template_param['default'] = parse_term(param.default, nsm=nsm) if len(param.default) > 0 else None
    return template_param

def parse_template_instance(parent_template_id, instance, nsm=None):
    """
        Parse a stOTTR template instance.

        Arguments:
            - parent_template_id ``int``: ID of the template that owns the scope of the instance.
            - instance ``str[]``: instance to parse
            - nsm :class`rdflib.namespace.NamespaceManager`: (optional) RDFlib namespace manager used to manage prefixes.

        Returns:
         A :class`ottr.base.AbstractTemplate`
    """
    template_name = parse_term(instance.name, nsm=nsm)

    # case 1: handle base templates (using a generic method)
    if template_name in BASE_TEMPLATES:
        TemplateConstructor, nb_arguments = BASE_TEMPLATES[template_name]
        if len(instance.arguments) != nb_arguments:
            raise Exception("The {} template takes exactly {} arguments, but {} were provided".format(template_name.n3(), nb_arguments, len(instance.arguments)))
        params = parse_instance_arguments(parent_template_id, instance.arguments, nsm=nsm)
        return TemplateConstructor(*params)

    # case 2: a non-base template instance
    return NonBaseInstance(template_name, parse_instance_arguments(parent_template_id, instance.arguments, nsm=nsm))

def parse_templates_stottr(text):
    """
        Parse a set of stOTTR template definitions and returns the list of all OTTR templates.

        Arguments:
            - text ``str``: stOTTR template definitions in text format.

        Returns:
            A list of :class`ottr.base.MainTemplate` built from the valid sOTTR template definitions provided as input.
    """
    # create a RDFLib NamespaceManager to handle automatic prefix expansion
    nsm = get_default_nsm()

    # run pOTTR lexer
    tree = lex_templates_stottr(text)

    # parse prefixes and register them into the NamespaceManager
    for prefix in tree.prefixes:
        uri = prefix.value
        if uri.startswith('<') and uri.endswith('>'):
            uri = uri[1: -1]
        nsm.bind(prefix.name, uri, replace=True)

    # parse each template definition found
    ottr_templates = list()
    # unique ID sued to make all variables unique to their scope
    template_id = 0
    for template in tree.templates:
        template_name = parse_term(template.name, nsm=nsm)

        # parse instances
        template_instances = [parse_template_instance(template_id, v, nsm=nsm) for v in template.instances]

        # create the OTTR template &
        ottr_template = MainTemplate(template_name, template_instances)
        # parse and register the template's parameters
        for position in range(len(template.parameters.asList())):
            parameter = parse_template_parameter(template_id, template.parameters[position], nsm=nsm)
            ottr_template.add_parameter(parameter['name'], position, param_type=parameter['type'], optional=parameter['optional'], nonblank=parameter['nonblank'], default=parameter['default'])
        # register the new OTTR template
        ottr_templates.append(ottr_template)
        template_id += 1
    return ottr_templates


def parse_instances_stottr(text):
    """
        Parse a set of stOTTR instances and returns them as objects.

        Arguments:
            - text ``str``: stOTTR instances in text format.

        Returns:
            A list of instances built from the valid sOTTR instances provided as input.
    """
    # create a RDFLib NamespaceManager to handle automatic prefix expansion
    nsm = get_default_nsm()

    # run pOTTR lexer
    tree = lex_instances_stottr(text)

    # parse prefixes and register them into the NamespaceManager
    for prefix in tree.prefixes:
        uri = prefix.value
        if uri.startswith('<') and uri.endswith('>'):
            uri = uri[1: -1]
        nsm.bind(prefix.name, uri, replace=True)

    # parse each OTTR instance found
    ottr_instances = list()
    for instance in tree.instances:
        ottr_instance = dict()
        ottr_instance['name'] = parse_term(instance.name, nsm=nsm)
        ottr_instance['arguments'] = list()
        # parse all instance's arguments
        # and save pairs (arguments's position, arguments's RDF value)
        for pos in range(len(instance.arguments)):
            arg = (pos, parse_term(instance.arguments[pos], nsm=nsm))
            ottr_instance['arguments'].append(arg)
        ottr_instances.append(ottr_instance)
    return ottr_instances
