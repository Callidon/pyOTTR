# expansion.py
# Author: Thomas MINIER - MIT License 2019
from ottr.base.template import AbstractTemplate

class CrossTemplate(AbstractTemplate):
    """A CrossTemplate expands a template instance using the 'cross' expansion mode."""

    def __init__(self, name, instance, cross_variable):
        super(CrossTemplate, self).__init__(name)
        self._inner_instance = instance
        self._cross_variable = cross_variable

    def expand(self, arguments, all_templates, bnode_suffix=(0, 0), as_nt=False):
        # assert that the cross variable is found in the arguments
        if self._cross_variable in arguments:
            # invoke inner instance with each value of the list variable
            for value in arguments[self._cross_variable]:
                # copy arguments and inject the local value for the cross variable
                local_args = dict()
                for k, v in arguments.items():
                    if k == self._cross_variable:
                        local_args[k] = value
                    else:
                        local_args[k] = v
                # recursively invoke the inner instance with the new set of arguments
                yield from self._inner_instance.expand(local_args, all_templates, bnode_suffix=bnode_suffix, as_nt=as_nt)
