Welcome to ottr's documentation!
================================

This library allows you to manipulate 
`OTTR Reasonable Ontology Templates <http://ottr.xyz/>`_ in Python.

Reasonable Ontology Templates (OTTR) is a language for representing ontology modelling patterns,
and is designed to support interaction with OWL or RDF knowledge bases at a higher level of abstraction, using modelling patterns rather than OWL axioms or RDF triples. This includes:

* building knowledge bases by instantiating templates;
* communicating (presenting, transferring and visualising) the knowledge base as a set of template instances at different levels of abstraction; and
* securing and improving the quality and sustainability of the knowledge base via structural and semantic analysis of the templates used to construct the knowledge base.

You can learn more about OTTR on the `official website <http://ottr.xyz/>`_.

Supported features
------------------

* `Definition and execution of templates <http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#2_Templates_and_Instances>`_ in the `stOTTR syntax <http://spec.ottr.xyz/stOTTR/0.1/>`_.
* `Nesting templates <http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#3_Nesting_templates>`_.
* `Type checking <http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#4_Types>`_.
* `Non blank <http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#5_NonBlank>`_, `Optional <http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#6_Optionals_and_None>`_ and `default values <http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#7_Default_values>`_ for template parameters.
* *RDF and RDFS templates* from the `OTTR template library <http://tpl.ottr.xyz/>`_ are loaded by default.

In development
--------------

* `Expansion modes <http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#8_Expansion_modes>`_.
* Support for `OWL templates <http://tpl.ottr.xyz/owl/>`_ from the template library.

Contents
--------
.. toctree::
  :maxdepth: 2

  quickstart
  ottr



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
