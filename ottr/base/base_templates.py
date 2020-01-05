# base_templates.py
# Author: Thomas MINIER - MIT License 2019-2020
from typing import Dict, Iterable, Tuple

from rdflib import URIRef

from ottr.base.argument import InstanceArgument
from ottr.base.template import AbstractTemplate
from ottr.base.utils import OTTR_TRIPLE_URI
from ottr.types import ExpansionResults, InputBindings


class OttrTriple(AbstractTemplate):
    """The default ottr:Triple base template, which expand to a RDF triple.

    Args:
      * subject_arg: Subject argument of the template instance.
      * predicate_arg: Predicate argument of the template instance.
      * object_arg: Object argument of the template instance.
    """

    def __init__(self, subject_arg: InstanceArgument, predicate_arg: InstanceArgument, object_arg: InstanceArgument):
        super(OttrTriple, self).__init__(OTTR_TRIPLE_URI)
        self._subject_arg = subject_arg
        self._predicate_arg = predicate_arg
        self._object_arg = object_arg

    def __str__(self) -> str:
        return f"ottr:Triple ({self._subject_arg}, {self._predicate_arg}, {self._object_arg}) :: BASE ."

    def __repr__(self) -> str:
        return self.__str__()

    def is_base(self) -> bool:
        """Returns True if the template is a base template, False otherwise"""
        return True

    def expand(self, arguments: InputBindings, all_templates: Dict[URIRef, AbstractTemplate], bnode_suffix: Tuple[int, int] = (0, 0), as_nt: bool = False) -> Iterable[ExpansionResults]:
        """Expands the template and yields a single RDF triple.

        Args:
          * arguments: Template instantation arguments.
          * all_templates: Map of all templates known at expansion times.
          * bnode_suffix: Pair of suffixes used for creating unique blank nodes.
          * as_nt: True if the RDF triples produced should be in n-triples format, False to use the rdflib format.

        Yields:
          A RDF triple, in rdflib or n-triples format.
        """
        yield (
            self._subject_arg.evaluate(bindings=arguments, bnode_suffix=bnode_suffix, as_nt=as_nt),
            self._predicate_arg.evaluate(bindings=arguments, bnode_suffix=bnode_suffix, as_nt=as_nt),
            self._object_arg.evaluate(bindings=arguments, bnode_suffix=bnode_suffix, as_nt=as_nt)
        )
