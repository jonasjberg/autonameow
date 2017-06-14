`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  
University mail: `js224eh[a]student.lnu.se`  

--------------------------------------------------------------------------------

`autonameow` TODO-list
======================

~~Please refer to the [Product
Backlog](https://github.com/1dv430/js224eh-project/wiki/backlog) for a current
listing.~~


High Priority
-------------

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

* __All data extraction is handled by `extractor` classes__ --
  `analyzer` classes do not perform any kind of data extraction.
* __The `Extraction` class controls all extractors__ --
  The first step in the processing pipeline is calling the extractors that are
  relevant to the current file.
    * Data produced by `extractor` classes is returned to a new separate
      container class `ExtractedData`.
* __The `Analysis` class controls all analyzers__ --
  Extracted data from `ExtractedData` is passed to the `Analysis` instance at
  init.  Then the analyzers relevant to the file is called to process the data
  returned by the extractors.
    * Data produced by `analyzer` classes is returned to a separate
      container in the `Analysis` class.
    * Overall program flow could go along the lines of:
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
* Move all existing code to the architecture described above.

### Internal data storage

* Think about distinguishing between *simple static data* and *derived data*.
    * __"Static data":__ string `test.pdf`
      (stored in results query field `filesystem.basename.full`)
    * __"Derived data":__ `datetime`-object extracted from a UNIX timestamp
      in `filesystem.basename.full`. Possibly stored as a dictionary with
      the `datetile`-object in `data['value']`, along with `weight`, etc.
    * Possibly additional types?
* Should the "simple static" information be collected in a separate run?
* Should the `Analysis` class `Results` instance only contain "simple static"
  data? If so, use a separate container for "derived data".
* Alternatively, store all types of results in the `Analysis` class `Results`
  instance but modify the `Results` class to distinguish between the types?


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
