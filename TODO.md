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

* `[TD0089]` Validate only "generic" data fields when reading config.

* `[TD0088]` Handle case where `ExtractedData.wrapper` is `None`.

* `[TD0082]` Integrate the `ExtractedData` class.

* `[TD0084]` Add handling collections (lists, etc) to the type wrapper classes.

* `[TD0066]` __Fix bad encoding of bytestring paths when listing results.__  
  When listing results with any of the `--list-*` options, paths are not
  displayed properly due to them not being handled properly before being passed
  to `yaml.dump` which performs the formatting of the results dict.

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

* `[TD0087]` Clean up messy and sometimes duplicated wrapping of "raw" data.


Medium Priority
---------------

* `[TD0098]` Use checksums as keys for cached data, not paths.

* `[TD0092]` Add tracking history and ability to "undo" renames.

* `[TD0054]` Represent datetime as UTC within autonameow. Convert incoming time
  to UTC and convert to local time as a final step before presentation or use.

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

* `[TD0014]` Possibly redesign high-level handling of a "configuration".
    * Decouple the `Configuration` instance from I/O.
    * Think about separating validation and parsing of incoming
      configuration data from the `Configuration` class.

* `[TD0015]` Allow conditionals in the configuration rules.
    * Test if a rule is applicable by evaluating conditionals.
        * Textual contents of the file matches a regular expression?
        * Some date/time-information lies within some specific range.

* `[TD0017]` Rethink how specified sources are connected to actual sources.
  Take for example the configuration rule:

    ```yaml
    RULES:
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

* `[TD0070]` Implement arbitrary common personal use case.

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

* `[TD0023]` Add additional option to force non-interactive mode (`--batch`?)

* `[TD0024]` Rework handling of unresolved operations
    * Instead of aborting if a rule data source is unavailable, use an
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

* `[TD0095]` Provide information on reporting bugs/issues.


Low Priority
------------

* `[TD0097]` Improve and fully implement caching to files on disk.

* `[TD0096]` Fix some replacements cause incorrect color highlighting.

* `[TD0091]` Take a look at old code in `util/dateandtime.py`.

* `[TD0068]` Let the user specify which languages to use for OCR.

* `[TD0059]` Replace `--list-datetime`, `--list-title` and `--list-all`
  with something more flexible like `--list {FIELD}`.

* `[TD0055]` Fully implement the `VideoAnalyzer` class.

* `[TD0026]` Implement safe handling of symbolic link input paths.

* __Add additional filetype-specific "extractors"__
    * `[TD0027]` __Word Documents__
        * Extract plain text and metadata from Word documents.
    * `[TD0028]` __E-books epub/mobi__
        * Extract metadata fields. Look into using `calibre`.
    * `[TD0064]` __E-books DjVu__
        * Extract plain text with `djvutxt`

* `[TD0029]` Add support for extracting MacOS Spotlight metadata (`mdls`)

* __Add additional plugins__
    * `[TD0030]` Plugin for querying APIs with ISBN numbers.
      (Already implemented in `autoname_pdf.py` and `isbn_query.py`)

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

* `[TD0039]` Do not include the rule attribute `score` when listing the
  configuration with `--dump-config`.

* `[TD0040]` Add assigning tags to GPS coordinates for tagging images with EXIF
  GPS data. Look into comparing coordinates with the
  [Haversine formula](http://en.wikipedia.org/wiki/Haversine_formula).

* `[TD0043]` Allow the user to tweak hardcoded settings using the
  configuration.

* `[TD0045]` Add ability to rename directories.

* `[TD0010]` Think about how data might need to be processed in multiple
  consecutive runs.
    * In relation to future weighting and prioritizing of analysis results.

* `[TD0011]` Think about how the overall "analysis" might be executed more than
  once.
    * Results from an initial analysis might be passed to the second analysis.
    * If a matched and active rule does not specify all required sources; the
      missing sources might be filled in by a more targeted approach using data
      gathered during the first run.

* `[TD0094]` __Search text for DOIs and query external services__  
  Example DOI: `10.1109/TPDS.2010.125`.  Could be used to query external
  services for publication metadata, as with ISBN-numbers.


Wishlist
--------

* Construct rules from user-specified __template__ and __filename__.

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
