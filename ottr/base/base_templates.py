# base_templates.py
# Author: Thomas MINIER - MIT License 2019
from ottr.base.template import AbstractTemplate
from ottr.base.utils import OTTR_TRIPLE_URI

class OttrTriple(AbstractTemplate):
    """
        The default ottr:Triple base template.
        In pratice, pyOTTR inline each template definition until it contains only instances of base templates (ottr:Triple and ottr:NullableTriple).
    """

    def __init__(self, subject_param, predicate_param, object_param):
        super(OttrTriple, self).__init__(OTTR_TRIPLE_URI)
        self._subject_param = subject_param
        self._predicate_param = predicate_param
        self._object_param = object_param

    def expand(self, parameters, as_nt=False):
        """Returns a generator that expands the template"""
        yield (
                self._subject_param.evaluate(bindings=parameters, as_nt=as_nt),
                self._predicate_param.evaluate(bindings=parameters, as_nt=as_nt),
                self._object_param.evaluate(bindings=parameters, as_nt=as_nt)
            )
