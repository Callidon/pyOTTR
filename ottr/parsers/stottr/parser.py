# parser.py
# Author: Thomas MINIER - MIT License 2019
from typing import Dict, List, Tuple, Union

from pyparsing import Group
from rdflib import Graph, URIRef, Variable
from rdflib.namespace import RDFS, NamespaceManager
from rdflib.util import from_n3

from ottr.base.argument import (ConcreteArgument, InstanceArgument,
                                VariableArgument)
from ottr.base.base_templates import OttrTriple
from ottr.base.expansion import CrossTemplate
from ottr.base.template import AbstractTemplate, MainTemplate, NonBaseInstance
from ottr.base.utils import OTTR_NONE, OTTR_TRIPLE_URI
from ottr.parsers.stottr.lexer import (lex_instances_stottr,
                                       lex_templates_stottr)
from ottr.types import Term

# All base templates are registered here,
# as tuples (template constructor, expected nb of arguments)
BASE_TEMPLATES = {
    OTTR_TRIPLE_URI: (OttrTriple, 3)
}


def unify_var(variable: Variable, suffix: Union[str, int]) -> Variable:
    """Makes a SPARQL Variable unique by appending a suffix to it.

    Args:
      * value: Variable to make unique.
      * suffix: suffix to append at the end of the value.
    Returns:
        A new SPARQL Variable
    """
    return Variable(f"{variable}_{suffix}")


def get_default_nsm() -> NamespaceManager:
    """Get an rdflib NamespaceManager with default prefixes configured"""
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


def parse_term(term: Union[str, List[str]], nsm: NamespaceManager = None) -> Term:
    """Parse a raw RDF term or a list of raw RDF Terms into the rdflib format.

    Args:
      * term: (List of) RDF Term(s) to parse (in n-triples format).
      * nsm: Namespace manager used to expand prefixed URIs.

    Returns:
      The parsed RDF term in rdflib format.
    """
    # case 1: a single RDf Term
    if type(term) == str:
        # the special keyword "none" is interpreted as "ottr:None"
        if term == "none":
            return OTTR_NONE
        # rdflib tends to see SPARQL variables as blank nodes, so we need to handle them separately
        if term.startswith('?'):
            return Variable(term[1:])
        return from_n3(term, nsm=nsm)
    else:  # Case 2: a list of RDF terms
        return [parse_term(value, nsm=nsm) for value in term]


def parse_instance_arguments(template_id: int, arguments: List[Term], nsm: NamespaceManager = None) -> List[InstanceArgument]:
    """Parse the arguments of a template instance.

    Args:
      * template_id: ID of the template.
      * arguments: instance arguments (RDF terms) to parse.
      * nsm: Namespace manager used to expand prefixed URIs.

    Retuns:
      A list of instance arguments.
    """
    args = list()
    for position in range(len(arguments)):
        value = arguments[position]
        if type(value) is Variable:
            args.append(VariableArgument(value, position))
        else:
            args.append(ConcreteArgument(value, position))
    return args


def parse_template_parameter(template_id: int, param: Group, nsm: NamespaceManager = None) -> Dict[str, Union[Term, bool]]:
    """Parse an OTTR template parameter.

    Args:
      * template_id: ID of the template.
      * param: Parameters to parse.
      * nsm: Namespace manager used to expand prefixed URIs.

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


def parse_template_instance(parent_template_id: int, instance: Group, nsm: NamespaceManager = None) -> AbstractTemplate:
    """Parse a stOTTR template instance.

    Arguments:
      * parent_template_id: ID of the template that owns the scope of the instance.
      * instance: instance to parse
      * nsm: Namespace manager used to expand prefixed URIs.

    Returns:
        An OTTR template.
    """
    cross_variable = None
    # if the instance uses a cross expansion
    if instance.type == "cross":
        # first, find the repeated variable
        classic_args = list()
        for pos in range(len(instance.content.arguments)):
            arg = instance.content.arguments[pos]
            if type(arg) is not str:
                cross_variable = parse_term(arg[0], nsm=nsm)
                classic_args.append(arg[0])
            else:
                classic_args.append(arg)
        # if not found, raise error
        # TODO improve error reporting
        if cross_variable is None:
            raise SyntaxError("Found an expansion mode 'cross' without a repeated variable.")
        # then, replace the current instance by the inner instance
        instance = instance.content
        instance.arguments = classic_args
    # TODO supports other expansion modes

    # parse arguments to RDF Terms
    ottr_arguments = list()
    for arg in instance.arguments:
        arg = parse_term(arg, nsm=nsm)
        # unify variables found during the process, so they are unique to the local scope
        if type(arg) is Variable:
            new_arg = unify_var(arg, parent_template_id)
            # replace the cross variable when it gets renammed
            if arg == cross_variable:
                cross_variable = new_arg
            arg = new_arg
        ottr_arguments.append(arg)

    # build the concrete template object
    template_name = parse_term(instance.name, nsm=nsm)
    ottr_instance = None

    # case 1: handle base templates (using a generic method)
    if template_name in BASE_TEMPLATES:
        TemplateConstructor, nb_arguments = BASE_TEMPLATES[template_name]
        if len(ottr_arguments) != nb_arguments:
            raise Exception(f"The {template_name.n3()} template takes exactly {nb_arguments} arguments, but {len(ottr_arguments)} were provided")
        params = parse_instance_arguments(parent_template_id, ottr_arguments, nsm=nsm)
        ottr_instance = TemplateConstructor(*params)
    else:
        # case 2: a non-base template instance
        ottr_instance = NonBaseInstance(template_name, parse_instance_arguments(parent_template_id, ottr_arguments, nsm=nsm))

    # use a cross expansion operator if needed
    if cross_variable is not None:
        cross_name = URIRef(f"http://pyOTTR?cross={template_name}")
        return CrossTemplate(cross_name, ottr_instance, cross_variable)
    return ottr_instance


def parse_templates_stottr(text: str) -> List[AbstractTemplate]:
    """Parse a set of stOTTR template definitions and returns the list of all OTTR templates.

    Argument: A set of stOTTR template definitions in text format.

    Returns: A list of OTTR templates built from the valid sOTTR template definitions provided as input.
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


def parse_instances_stottr(text: str) -> List[Dict[str, Union[Term, List[Tuple[int, Term]]]]]:
    """Parse a set of stOTTR instances and returns them as objects.

    The objects returned are expected to be used with the `format_arguments` method of a template.

    Argument: Set of stOTTR instances in text format.

    Returns: A list of instances built from the valid sOTTR instances provided as input.
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
            argument = (pos, parse_term(instance.arguments[pos], nsm=nsm))
            ottr_instance['arguments'].append(argument)
        ottr_instances.append(ottr_instance)
    return ottr_instances
