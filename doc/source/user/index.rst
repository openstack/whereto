===========
Users guide
===========

To test a set of redirects, ``whereto`` needs the input ``.htaccess``
file and another input file with test data.

The ``.htaccess`` file should contain ``Redirect`` and
``RedirectMatch`` directives. Blank lines and lines starting with
``#`` are ignored. For example, this input includes 6 rules:

.. code-block:: text

   # Redirect old top-level HTML pages to the version under most recent
   # full release.
   redirectmatch 301 ^/$ /pike/
   redirectmatch 301 ^/index.html$ /pike/
   redirectmatch 301 ^/openstack-projects.html$ /pike/projects.html
   redirectmatch 301 ^/language-bindings.html$ /pike/language-bindings.html

   # Redirect docs.openstack.org index.html subpage pointers to main page
   redirect 301 /install/ /pike/install/
   redirect 301 /basic-install/ /pike/install/

The test data file should include one test per line, including 3
parts: the input path, the expected HTTP response code, and the
expected output path. For example:

.. code-block:: text

   / 301 /pike/
   / 301 /pike
   /install/ 301 /pike/install/
   /no/rule 301 /should/fail

The output from ``whereto`` includes a report of any tests that do not
match, including if no rules match and if multiple rules match. For
example:

.. code-block:: console

   $ whereto -q --ignore-untested .htaccess test.txt

   Test on line 2 did not produce expected result: / 301 /pike
     [7] redirectmatch 301 ^/$ /pike/
   No rule matched test on line 4: /no/rule 301 /should/fail

   2 failures
