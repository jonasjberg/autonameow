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

* `[TD0004]` __Text encoding issues__
    * Enforce strict boundaries between all external systems and an internal
      text data representation.
    * Store original filename parts as both bytestrings and the internal
      representation?  If the user wants to use a part of the original file
      name in the result, the conversion can not be lossy. Best way to prevent
      issues is to store bytestrings and perform any processing on copies that
      have __not__ been converted to the internal format?

* `[TD0005]` __Internal "API"__ -- communication between modules
    * Replace the old way of calling the analyzer `get_{fieldname}` methods
      with passing the `Analysis` class method `collect_results` as a callback.
    * Fully implement the idea of dynamically constructing structures and
      interfaces from a single reference data structure at runtime.

* `[TD0006]` __New high-level architecture__
    * Move to use the redesigned architecture
    * All data extraction is handled by `extractor` classes
    * `analyzer` classes do not perform any kind of data extraction.
    * Plan for optimization by not extracting more data than necessary.
      How could this be implemented?

* `[TD0044]` __Rework converting "raw data" to internal representations__
    * Converting raw data to internal representations is currently implemented
      very poorly and must be reworked.
    * Think about how to handle translation in the "general" sense; high-level,
      abstract. Would it be wise to let data extractors convert raw data to
      internal types? (For example; messy OCR text to `datetime` object)
        * A "general solution" using some new entity tasked with translating
          data *might be too "general"* considering the likely granularity of
          operations needed to perform the conversion.  That is, if the
          required operations differs greatly between data sources, abstracting
          the process would mostly add yet another layer of indirection ..
    * Think about how wrapped data types (`[TD0002]`) relates to this.


Medium Priority
---------------

* `[TD0052]` Analyzer classes should provide their respective "query strings".

* `[TD0051]` Implement or remove the `CommonFileSystemExtractor` class.

* `[TD0050]` Figure out how to represent "null" for `datetime` types.

* `[TD0049]` __Think about defining legal "placeholder fields".__
  Might be helpful to define all legal fields (such as `title`, `datetime`,
  `author`, etc.) somewhere and keep references to type coercion wrappers,
  maybe validation and/or formatting functionality; in the field definitions.

* `[TD0008]` Simplify installation.
    * Add support for `pip` or similar package manager.

* `[TD0009]` Implement proper plugin interface
    * Have plugins "register" themselves to a plugin handler?
    * Querying plugins might need some translation layer between the
      `autonameow` field naming convention and the specific plugins naming
      convention. For instance, querying a plugin for `title` might require
      actually querying the plugin for `document:title` or similar.
    * Abstract base class for all plugins;
        * Means of providing input data to the plugin.
        * Means of executing the plugin.
        * Means of querying for all or a specific field.

* `[TD0010]` Think about how data might need to be processed in multiple
  consecutive runs.
    * In relation to future weighting and prioritizing of analysis results.

* `[TD0011]` Think about how the overall "analysis" might be executed more than
  once.
    * Results from an initial analysis might be passed to the second analysis.
    * If a matched and active rule does not specify all required sources; the
      missing sources might be filled in by a more targeted approach using data
      gathered during the first run.

* `[TD0012]` Add some type of caching.
    * Extracting text from a PDF should only have to happen once, at most.
      Preferably not at all, unless a rule conditional tests the text content
      or the text is needed elsewhere.
    * Image OCR is very slow, should only be executed when needed, caching the
      results for all accesses.

* `[TD0013]` Add conditional data extraction.
    * Extractors should not run unless needed. Related to caching, above.

* `[TD0014]` Possibly redesign high-level handling of a "configuration".
    * Decouple the `Configuration` instance from I/O.
    * Think about separating validation and parsing of incoming
      configuration data from the `Configuration` class.

* `[TD0015]` Allow conditionals in the configuration file rules.
    * Test if a file rule is applicable by evaluating conditionals.
        * Textual contents of the file matches a regular expression?
        * Some date/time-information lies within some specific range.

* `[TD0017]` Rethink how specified sources are connected to actual sources.
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

* `[TD0018]` There are more cases like the above that should be thought about.
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

* `[TD0041]` Improve data filtering prior to name assembly in `NameBuilder`

* `[TD0019]` Rework the `FilenameAnalyzer`
    * `[TD0020]` Identify data fields in file names.
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

* `[TD0021]` Look into merging possibly redundant methods `get` and `query` in
  the `AnalysisResults` class.

* `[TD0022]` Look into merging possibly redundant methods `get` and `query` in
  the `ExtractedData` class.

* `[TD0023]` Add additional option to force non-interactive mode (`--batch`?)

* `[TD0024]` Rework handling of unresolved operations
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

* `[TD0025]` Add additional option to force interactive mode (`--interactive`?)
    * This mode would require the user to confirm actions/choices (which?)


Low Priority
------------

* `[TD0026]` Implement safe handling of symbolic link input paths.

* __Add additional filetype-specific "extractors"__
    * `[TD0027]` __Word Documents__
        * Extract plain text and metadata from Word documents.
    * `[TD0028]` __E-books epub/mobi__
        * Extract metadata fields. Look into using `calibre`.

* `[TD0029]` Add support for extracting MacOS Spotlight metadata (`mdls`)

* __Add additional plugins__
    * `[TD0030]` Plugin for querying APIs with ISBN numbers.
      (Already implemented in `autoname_pdf.py` and `isbn_query.py`)

* `[TD0032]` Add support for UNIX-style globs in path fields in the
  configuration.

* `[TD0033]` Refactor unit tests.
    * Mitigate superlinear increase in unit test execution speed.
    * Try to rewrite tests that operate on actual files
        * Cache results from expensive calls, avoid repeated actions.
        * Substitute I/O-operations with some kind of mocking.

* __Look into filtering__
    * Think about the concept of filtering data at a high-level.
    * Who should be able to control filtering?
        * The user? Through the configuration?
        * Various parts of the program? Part of the file analysis or data
          extraction pipeline?
    * `[TD0034]` Redesign overall filtering.
    * `[TD0035]` Rewrite the `ResultFilter` class or substitute with something
      else.

* `[TD0036]` Allow specifying known good candidates for fields.
    * For instance, a list of known book publishers. Possibly a dictionary
      where keys are preferred book publishers, and each key stores a
      list of possible search strings that should be replace with the key.

* `[TD0037]` Improve "filetags" integration.
    * For instance, the Microsoft Vision API returns *a lot* of tags,
      too many to use in a filename without any kind of selection process.
    * It would be very useful to be able to filter tags by getting the
      intersection of the unfiltered tags and a whitelist.
    * Allow specifying allowed tags in the configuration?
    * Allow specifying mutually exclusive tags in the configuration?

* `[TD0038]` Add new name format placeholder field `{year}`.

* `[TD0039]` Do not include the file rule attribute `score` when listing the
  configuration with `--dump-config`.

* `[TD0040]` Add assigning tags to GPS coordinates for tagging images with EXIF
  GPS data.

* `[TD0042]` Respect the `--quiet` option. Suppress (all but critical?) output.

* `[TD0043]` Allow the user to tweak hardcoded settings using the
  configuration.

* `[TD0045]` Add ability to rename directories.

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
