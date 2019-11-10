# base_templates.py
# Author: Thomas MINIER - MIT License 2019
from ottr.base.template import AbstractTemplate
from ottr.base.parameter import URIParameter
from ottr.base.utils import OTTR_LABEL_URI, OTTR_TRIPLE_URI, OTTR_TYPE_URI
from rdflib.namespace import RDF, RDFS

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

    def is_base(self):
        """Returns True if the template is a base template, False otherwise"""
        return True

    def expand(self, parameters, all_templates, as_nt=False):
        """Returns a generator that expands the template"""
        yield (
                self._subject_param.evaluate(bindings=parameters, as_nt=as_nt),
                self._predicate_param.evaluate(bindings=parameters, as_nt=as_nt),
                self._object_param.evaluate(bindings=parameters, as_nt=as_nt)
            )

class OttrType(OttrTriple):
    """The o-rdf:Type base template, equivalent to ottr:Triple(?s, rdf:type, ?type)"""

    def __init__(self, subject_param, object_param):
        super(OttrType, self).__init__(subject_param, URIParameter(RDF.type, 1), object_param)
        self._name = OTTR_TYPE_URI

class OttrLabel(OttrTriple):
    """The o-rdfs:Label base template, equivalent to ottr:Triple(?s, rdfs:label, ?type)"""

    def __init__(self, subject_param, object_param):
        super(OttrLabel, self).__init__(subject_param, URIParameter(RDFS.label, 1), object_param)
        self._name = OTTR_LABEL_URI
