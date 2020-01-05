# expansion.py
# Author: Thomas MINIER - MIT License 2019-2020
from typing import Dict, Iterable, Tuple

from rdflib import URIRef, Variable

from ottr.base.template import AbstractTemplate
from ottr.types import ExpansionResults, InputBindings


class CrossTemplate(AbstractTemplate):
    """A CrossTemplate expands a template instance using the 'cross' expansion mode.

    Args:
      * name: Template's name.
      * instance: Template instance to expand with the 'cross' expansion mode.
      * cross_variable: Variable which binds to the list of arguments for the cross-operator.
    """

    def __init__(self, name: URIRef, instance: AbstractTemplate, cross_variable: Variable):
        super(CrossTemplate, self).__init__(name)
        self._inner_instance = instance
        self._cross_variable = cross_variable

    def expand(self, arguments: InputBindings, all_templates: Dict[URIRef, AbstractTemplate], bnode_suffix: Tuple[int, int] = (0, 0), as_nt: bool = False) -> Iterable[ExpansionResults]:
        """Expands the template and yields RDF triples.

        Args:
          * arguments: Template instantation arguments.
          * all_templates: Map of all templates known at expansion times.
          * bnode_suffix: Pair of suffixes used for creating unique blank nodes.
          * as_nt: True if the RDF triples produced should be in n-triples format, False to use the rdflib format.

        Yields:
          RDF triples, in rdflib or n-triples format.
        """
        # assert that the cross variable is found in the arguments
        if self._cross_variable in arguments:
            # invoke inner instance with each value of the list variable
            for value in arguments[self._cross_variable]:
                # copy arguments and inject the local value for the cross variable
                local_args: InputBindings = dict()
                for k, v in arguments.items():
                    if k == self._cross_variable:
                        local_args[k] = value
                    else:
                        local_args[k] = v
                # recursively invoke the inner instance with the new set of arguments
                yield from self._inner_instance.expand(local_args, all_templates, bnode_suffix=bnode_suffix, as_nt=as_nt)
