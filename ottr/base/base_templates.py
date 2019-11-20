# base_templates.py
# Author: Thomas MINIER - MIT License 2019
from ottr.base.template import AbstractTemplate
from ottr.base.utils import OTTR_TRIPLE_URI


class OttrTriple(AbstractTemplate):
    """
        The default ottr:Triple base template.
    """

    def __init__(self, subject_arg, predicate_arg, object_arg):
        super(OttrTriple, self).__init__(OTTR_TRIPLE_URI)
        self._subject_arg = subject_arg
        self._predicate_arg = predicate_arg
        self._object_arg = object_arg

    def __str__(self):
        return f"ottr:Triple ({self._subject_arg}, {self._predicate_arg}, {self._object_arg}) :: BASE ."

    def __repr__(self):
        return self.__str__()

    def is_base(self):
        """Returns True if the template is a base template, False otherwise"""
        return True

    def expand(self, arguments, all_templates, bnode_suffix=(0, 0), as_nt=False):
        """Returns a generator that expands the template"""
        yield (
            self._subject_arg.evaluate(bindings=arguments, bnode_suffix=bnode_suffix, as_nt=as_nt),
            self._predicate_arg.evaluate(bindings=arguments, bnode_suffix=bnode_suffix, as_nt=as_nt),
            self._object_arg.evaluate(bindings=arguments, bnode_suffix=bnode_suffix, as_nt=as_nt)
        )
