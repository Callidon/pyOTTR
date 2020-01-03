Quickstart
================

Installation
-------------

**Using pip (recommended)**

.. code-block:: bash

  pip install ottr

**Manual installation**

*Requirement:* `poetry <https://python-poetry.org/>`_ (v0.12 or higher).

.. code-block:: bash

  git clone https://github.com/Callidon/pyOTTR.git
  cd pyOTTR/
  poetry install


Getting started
----------------

The main class to manipulate is `OttrGenerator`, which is used to load OTTR templates and expand template instances.
So, in practice, you only need to create a new generator, load some templates and then execute your instances to produce RDF triples.
Otherwise, everything else is done using classic OTTR syntax!

By default, **all templates** from the `OTTR template library <http://tpl.ottr.xyz/>`_ are loaded when the generator is created.

.. code-block:: python

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
