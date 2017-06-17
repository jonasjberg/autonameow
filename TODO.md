`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  
University mail: `js224eh[a]student.lnu.se`  

--------------------------------------------------------------------------------

`autonameow` TODO-list
======================


High Priority
-------------

* Update `MimeTypeConfigFieldParser` to handle MIME type globbing.

### Text encoding issues

* Enforce strict boundaries between all external systems and an internal text
  data representation.
* Add reusable translation layer that ensures proper handling of text encoding
  of *all incoming textual data*; standard input/output/error/.., path/file
  names, contents of text files, etc.
* Add corresponding reusable translation layer for *all outgoing textual data*.

### Internal "API" -- communication between modules

* Replace the old way of calling the analyzer `get_{fieldname}` methods
  with passing the `Analysis` class method `collect_results` as a callback.
* Fully implement the idea of dynamically constructing structures and
  interfaces from a single reference data structure at runtime.

### New high-level architecture:

* Move all existing code to the architecture described below.
* __All data extraction is handled by `extractor` classes__ --
  `analyzer` classes do not perform any kind of data extraction.
    * Should data produced by `analyzer` classes be returned to a separate
      container in the `Analysis` class?
* Modify high-level program flow to something along the lines of:
    1. Load configuration
    2. Run all extractors that can handle the given file
    3. Determine which configuration rule matches the given file
    4. Enqueue analyzers based on the rule and extracted data
    5. Run all enqueued analyzers
    6. Assemble new file name from all available data

    Having the extractor data available when evaluating rules (3) solves
    the problem of evaluating certain conditions, like testing if the
    given file contains a specific line of text, etc.
* Plan for optimization by not extracting more data than necessary.
  How could this be implemented?
* Converting strings to `datetime` objects and similar translation of metadata
  fields should be handled by the extractors. It is currently mostly done in
  the analyzers.


Medium Priority
---------------

* Simplify installation.
    * Add support for `pip` or similar package manager.

* Implement proper plugin interface
    * Have plugins "register" themselves to a plugin handler?
    * Querying plugins might need some translation layer between the
      `autonameow` field naming convention and the specific plugins naming
      convention. For instance, querying a plugin for `title` might require
      actually querying the plugin for `document:title` or similar.
    * Abstract base class for all plugins;
        * Means of providing input data to the plugin.
        * Means of executing the plugin.
        * Means of querying for all or a specific field.

* Think about how data might need to be processed in multiple consecutive runs.
    * In relation to future weighting and prioritizing of analysis results.

* Think about how the overall "analysis" might be executed more than once.
    * Results from an initial analysis might be passed to the second analysis.
    * If a matched and active rule does not specify all required sources; the
      missing sources might be filled in by a more targeted approach using data
      gathered during the first run.

* Add some type of caching.
    * Extracting text from a PDF should only have to happen once, at most.
      Preferably not at all, unless a rule conditional tests the text content
      or the text is needed elsewhere.
    * Image OCR is very slow, should only be executed when needed, caching the
      results for all accesses.

* Add conditional data extraction.
    * Extractors should not run unless needed. Related to caching, above.

* Refactor the 'Configuration' class. Look over all of 'configuration.py'.



Low Priority
------------

* Add additional filetype-specific "extractors".
    * __Word Documents__
        * Extract plain text and metadata from Word documents.
    * __E-books epub/mobi__
        * Extract metadata fields. Look into using `calibre`.

* Add support for extracting MacOS Spotlight metadata (`mdls`)

* Add additional plugins.
    * Plugin for querying APIs with ISBN numbers.
      (Already implemented in `autoname_pdf.py` and `isbn_query.py`)

* Add compatibility checks when loading configuration.


Wishlist
--------

* Construct file rules from user-specified __template__ and __filename__.

    The user specifies a expected __file name template__ and
    a __expected file name__ for a given file;

    ```
       Given the file:  "cats-tale.pdf"
     Desired Template:  {datetime} {title} -- {tags}.{extension}
    Expected Filename:  "2017-06-10T224655 A Cats Taile -- gibson biography.pdf"
    ```

    The program should then figure out *which data* from *which sources*
    should be used to construct the expected file name.

    A suitable rule that reproduces the expected result should be generated
    and added to the user configuration.

* Add API for developing GUI wrappers and web frontends.
