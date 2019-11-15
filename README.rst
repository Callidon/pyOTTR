pyOTTR
======

Manipulate `OTTR Reasonable Ontology Templates`_ in Python.

`Package documentation`_

`OTTR documentation`_

**Supported features:**

* `Definition and execution of templates`_ in the `stOTTR syntax`_
* `Nesting templates`_
* `Type checking`_
* `Non blank`_, `Optional`_ and `default values`_ for template parameters.
* *RDF and RDFS templates* from the `OTTR template library`_ are loaded by default.


**In development:**

* `Expansion modes`_
* Support for `OWL templates`_ from the template library


Installation
============

Using pip (recommended)
-----------------------

::

   pip install ottr

Manual installation
-------------------

::

   git clone
   cd pyOTTR/
   python setup.py install

Getting started
===============

The main class to manipulate is ``OttrGenerator``, which is used to load
OTTR templates and expand template instances. So, in practice, you only
need to create a new generator, load some templates and then execute
your instances to produce RDF triples.

By default, **all templates** from the `OTTR template
library <http://tpl.ottr.xyz/>`__ are loaded when the generator is
created.

.. code:: python

     from ottr import OttrGenerator
     # An OttrGenerator is used to load templates and expand instances
     generator = OttrGenerator()

     # Load a simple OTTR template definition
     generator.load_templates("""
       @prefix ex: <http://example.org#>.

       ex:FirstName [ottr:IRI ?uri, ?firstName] :: {
         ottr:Triple (?uri, foaf:firstName, ?firstName )
       } .

       ex:Person[ ?firstName ] :: {
         ottr:Triple (_:person, rdf:type, foaf:Person ),
         ex:FirstName (_:person, ?firstName)
       } .
     """)

     # Parse and prepare an instance for execution
     instances = generator.instanciate("""
       @prefix ex: <http://example.org#>.

       ex:Person("Ann").
     """)

     # Execute the instance, which yield RDF triples
     # The following prints (_:person0, rdf:type, foaf:Person) and (_:person0, foaf:firstName, "Ann")
     for s, p, o in instances.execute(as_nt=True):
       print("# ----- RDF triple ----- #")
       print((s, p, o)

.. _OTTR Reasonable Ontology Templates: http://ottr.xyz/
.. _Package documentation: https://callidon.github.io/pyOTTR
.. _OTTR documentation: http://ottr.xyz/
.. _Definition and execution of templates: http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#2_Templates_and_Instances
.. _stOTTR syntax: http://spec.ottr.xyz/stOTTR/0.1/
.. _Nesting templates: http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#3_Nesting_templates
.. _Type checking: http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#4_Types
.. _Non blank: http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#5_NonBlank
.. _Optional: http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#6_Optionals_and_None
.. _default values: http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#7_Default_values
.. _OTTR template library: %5Bhttp://tpl.ottr.xyz/%5D
.. _Expansion modes: http://spec.ottr.xyz/pOTTR/0.1/01-basics.html#8_Expansion_modes
.. _OWL templates: http://tpl.ottr.xyz/owl/
