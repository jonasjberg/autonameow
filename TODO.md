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

* __Refactor the `Configuration` class__
    * Look over all of `configuration.py`.
    * Fix `eval_condition` in `core/evaluate/rulematcher.py`.
    * Think about adding a custom type system in order to control configuration
      parsing, evaluating file rule conditions and overall internal handling of
      data.
        * Types could fall back to safe defaults, avoid countless permutations
          of "None-checking".
        * Type classes could implement comparison/matching methods.

* __Implement gathering data for configuration validation at run-time__
    * Have extractors register themselves at run-time.
    * Collect valid extractor query strings at run-time.
    * Have analyzers register themselves at run-time.
    * Collect valid analyzer query strings at run-time.
    * Rework configuration validation to use dynamically updated tests.
    * Replace hard coded strings with gathered data.

* __Text encoding issues__
    * Enforce strict boundaries between all external systems and an internal
      text data representation.
    * Store original filename parts as both bytestrings and the internal
      representation?  If the user wants to use a part of the original file
      name in the result, the conversion can not be lossy. Best way to prevent
      issues is to store bytestrings and perform any processing on copies that
      have __not__ been converted to the internal format?

* __Internal "API"__ -- communication between modules
    * Replace the old way of calling the analyzer `get_{fieldname}` methods
      with passing the `Analysis` class method `collect_results` as a callback.
    * Fully implement the idea of dynamically constructing structures and
      interfaces from a single reference data structure at runtime.

* __New high-level architecture__ -- Move to use the redesigned architecture
    * All data extraction is handled by `extractor` classes
    * `analyzer` classes do not perform any kind of data extraction.
    * Plan for optimization by not extracting more data than necessary.
      How could this be implemented?
    * Converting strings to `datetime` objects and similar translation of
      metadata fields should be handled by the extractors. It is currently
      mostly done in the analyzers.

* Pass all data to the `RuleMatcher` instance. Currently, only the analysis
  data and data stored in the `FileObject` is available when evaluating the
  rules. This hasn't been an obvious problem due to the fact that the current
  implementation of rule evaluation is so primitive and basic.


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

* Possibly redesign high-level handling of a "configuration".
    * Decouple the `Configuration` instance from I/O.
    * Think about separating validation and parsing of incoming
      configuration data from the `Configuration` class.

* Allow conditionals in the configuration file rules.
    * Test if a file rule is applicable by evaluating conditionals.
        * Textual contents of the file matches a regular expression?
        * Some date/time-information lies within some specific range.

* __Enforce consistency in the configuration syntax.__
  For example, why does the conditions for a file rule specify `extension`
  under `filesystem`, while the results data structure has `extension` nested
  under `filesystem.basename.extension`.

* Rethink how specified sources are connected to actual sources.
  Take for example the configuration file rule:

    ```yaml
    FILE_RULES:
    -   CONDITIONS:
            contents:
                mime_type: image/*
            filesystem:
                pathname: ~/Dropbox/Camera Uploads/.*
        DATA_SOURCES:
            extension: contents.mime_type
    ```
  This will fail, or *should fail* as MIME types on the form `image/jpeg`,
  `image/png`, etc can't be used as a file extension without some
  pre-processing -- converting `image/png` to `png`.

* There are more cases like the above that should be thought about.
  A common case is the slight modification to the current file name.
  Original file name:
    ```
    2017-06-20_00-49-56 Working on autonameow.png
    ```
  Desired file name:
    ```
    2017-06-20T004956 Working on autonameow.png
    ```
  How should this be specified in the configuration?
  A simple alternative is to specify the filename analyzer as the source.
  The `DATETIME_FORMAT` makes sure that the timestamp format is changed.

    ```yaml
    FILE_RULES:
    -   DATA_SOURCES:
            extension: contents.basename.extension
            datetime: analysis.filename.{?????}
            title: filesystem.basename.prefix
        NAME_FORMAT: "{datetime} {title}.{extension}"
    DATETIME_FORMAT:
        datetime: '%Y-%m-%dT%H%M%S'
    ```
  But this is not configurable -- how would the filename analyzer know
  which of many possible datetime results to use?

* Rework the `FilenameAnalyzer`
    * Identify data fields in file names.
        ```
        screencapture-github-jonasjberg-autonameow-1497964021919.png
        ^___________^ ^__________________________^ ^___________^
             tag            title/description        timestamp
        ```
        * Use some kind of iterative evaluation; split into parts at
          separators, assign field types to the parts and find a "best fit".
          Might have to try several times at different separators, re-evaluting
          partials after assuming that some part is a given type, etc.
        * __This is a non-trivial problem__, I would rather not re-implment
          existing solutions poorly.
        * Look into how `guessit` does it or possibility of modifying
          `guessit` to identify custom fields.

* Look into merging possibly redundant methods `get` and `query` in the
  `AnalysisResults` class.

* Look into merging possibly redundant methods `get` and `query` in the
  `ExtractedData` class.

* Add additional option to force __non-interactive mode__ (`--batch`?)

* Rework handling of unresolved operations
    * Instead of aborting if a file rule data source is unavailable, use an
      *interactive mode* and ask the user how to proceed.
    * Ideally, any remaining processing should proceed in the background. The
      user should be able to begin processing a large number of files without
      having to worry about checking for prompts.
    * Unresolved tasks could be enqueued and paused while waiting for the user
      to respond. Tasks that are able to finish without user interaction should
      keep working in the background.
    * The option to force non-interactive mode would be used to get the current
      behaviour; skipping files that can not be processed due to unavailable
      sources or multiple conflicting options, etc.

* Add additional option to force __interactive mode__ (`--interactive`?)
    * This mode would require the user to confirm actions/choices (which?)


Low Priority
------------

* Implement safe handling of symbolic link input paths.

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

* Add support for UNIX-style globs in path fields in the configuration.

* Refactor unit tests.
    * Mitigate superlinear increase in unit test execution speed.
    * Try to rewrite tests that operate on actual files
        * Cache results from expensive calls, avoid repeated actions.
        * Substitute I/O-operations with some kind of mocking.

* Look into filtering.
    * Think about the concept of filtering data at a high-level.
    * Who should be able to control filtering?
        * The user? Through the configuration?
        * Various parts of the program? Part of the file analysis or data
          extraction pipeline?
    * Redesign overall filtering.
    * Rewrite the `ResultFilter` class or substitute with something else.

* Allow specifying known good candidates for fields.
    * For instance, a list of known book publishers. Possibly a dictionary
      where keys are preferred book publishers, and each key stores a
      list of possible search strings that should be replace with the key.

* Improve "filetags" integration.
    * For instance, the Microsoft Vision API returns *a lot* of tags,
      too many to use in a filename without any kind of selection process.
    * It would be very useful to be able to filter tags by getting the
      intersection of the unfiltered tags and a whitelist.
    * Allow specifying allowed tags in the configuration?
    * Allow specifying mutually exclusive tags in the configuration?

* Add new name format placeholder field `{year}`.

* Do not include the file rule attribute `score` when listing the
  configuration with `--dump-config`.

* Add assigning tags to GPS coordinates for tagging images with EXIF GPS data.


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
