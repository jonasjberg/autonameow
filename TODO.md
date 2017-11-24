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

* `[TD0115]` __Clear up uncertainties about data multiplicities.__  
  I.E. list of data dicts vs. single data dict that contains a list
  of data (`multivalued: True`).

* `[TD0100]` Spec out "operating modes" and functionality requirements.

* `[TD0099]` Use `python-prompt-toolkit` for the interactive cli UI.

* `[TD0089]` Validate only "generic" data fields when reading config.

* `[TD0066]` __Fix bad encoding of bytestring paths when listing results.__  
  When listing results with any of the `--list-*` options, paths are not
  displayed properly due to them not being handled properly before being passed
  to `yaml.dump` which performs the formatting of the results dict.

* `[TD0102]` Fix inconsistencies in results passed back by analyzers.

* `[TD0108]` Fix inconsistencies in results passed back by plugins.

* `[TD0126]` Clean up boundaries/interface to the `analyzers` package.

* `[TD0127]` Clean up boundaries/interface to the `extractors` package.

* `[TD0128]` Clean up boundaries/interface to the `plugins` package.

* `[TD0129]` Enforce passing validated data to `NameTemplateField.format()`.


Medium Priority
---------------

* `[TD0112]` __Handle merging "equivalent" data in the `Resolver`.__  
  Add some sort of system for normalizing entities.
  Example of problem this is intended to solve:
    ```
    [WARNING]  Not sure what data to use for field "<class 'core.namebuilder.fields.Author'>"..
    [WARNING]  Field candidate 000 :: "['G. C. Sjöberg']"
    [WARNING]  Field candidate 001 :: "['Gibson C. Sjöberg']"
    [WARNING]  Not sure what data to use for field "<class 'core.namebuilder.fields.Title'>"..
    [WARNING]  Field candidate 000 :: "Everyday Fur And Statistics: Meow, Kibble, Dogs And War"
    [WARNING]  Field candidate 001 :: "Everyday Fur And Statistics Meow, Kibble, Dogs And War"
    ```

* `[TD0111]` Add abstraction between user interaction and CLI specifics.

* `[TD0107]` Get platform-specific default paths for persistent storage.

* `[TD0104]` Merge duplicate candidates and re-normalize probabilities.

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

    * `[TD0110]` Improve finding probable date/time in file names.
        * Provide a single most probable result.
        * Rank formats: `YMD` (EU), `MDY` (US), `DMY` (parts of EU, Asia), etc.
        * Look at any surrounding __context__ of files.

            For instance, given a directory containing files:
            ```
            foo_08.18.17.txt
            bar_11.04.16.txt
            ```
            The date components of `bar_11.04.16.txt` can not be clearly
            determined. Many possible date formats could work.

            But `foo_08.18.17.txt` can only be successfully parsed with the
            date format `foo_MM.DD.YY`.
            *(18 is probably not the future year 2018, but 08 might be 2008..)*

            This information could be used to weight this format higher to
            help improve the results of parsing `foo_08.18.17.txt`.

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

* `[TD0125]` __Add aliases (generics) for MeowURI leafs__
  Should probably provide a consistent internal alternative field name when
  specifying extractor-specific MeowURIs, not only with "generic".
  Example of equivalent MeowURIs with the "alias" or "generic":
    ```
    extractor.metadata.exiftool.PDF:CreateDate
    extractor.metadata.exiftool.date_created
    ```
  Another example:
    ```
    extractor.metadata.exiftool.EXIF:DateTimeOriginal
    extractor.metadata.exiftool.date_created
    ```
  The examples illustrate that multiple provider-specific fields would have to
  share a single "alias" or "generic", because there will always be fewer of
  them. If these were not based on the subclasses of `GenericField`, they could
  simply be made to map directly with the provider fields, maybe only with a
  slight transformation like converting to lower-case.
  Example of alternative using simple transformations:
    ```
    extractor.metadata.exiftool.EXIF:DateTimeOriginal
    extractor.metadata.exiftool.exif_datetimeoriginal
    ```

* `[TD0124]` Add option (script?) to run failed regression tests manually.

* `[TD0121]` Create a script for generating regression tests.

* `[TD0118]` Improve robustness and refactor searching text for editions.

* `[TD0114]` Improve the `EbookAnalyzer`.

* `[TD0113]` Fix exceptions not being handled properly (?)

* `[TD0109]` __Allow arbitrary name template placeholder fields.__  
    It is currently difficult to use a rule similar to this:
    ```
    TV-series:
        CONDITIONS:
            extractor.filesystem.xplat.pathname.full: '/tank/media/tvseries'
            extractor.filesystem.xplat.contents.mime_type: video/*
        NAME_FORMAT: '{title} S{season}E{episode}.{extension}'
        DATA_SOURCES:
            title: plugin.guessit.title
            season: plugin.guessit.season
            episode: plugin.guess.episode
            extension: extractor.filesystem.xplat.contents.mime_type
        exact_match: true
    ```

    This rule gives the following error:
    ```
    [ERROR] Bad rule "TV-series"; uses invalid name template format
    ```
    This could be solved by either adding `{season}` and `{episode}` as new
    template fields or by allowing arbitrary placeholder fields with some
    simple format like `{a}`, `{b}`, etc.

* `[TD0101]` __Add ability to limit sizes of persistent storage/caches.__  
  Store timestamps with stored data and remove oldest entries when exceeding
  the file size limit.

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
     Desired Template:  {datetime} {title} -- {tags}.{extension}
    Expected Filename:  "2017-06-10T224655 A Cats Taile -- gibson biography.pdf"
    ```

    The program should then figure out *which data* from *which sources*
    should be used to construct the expected file name.

    A suitable rule that reproduces the expected result should be generated
    and added to the user configuration.

* Add API for developing GUI wrappers and web frontends.


Windows-compatibility *(Very Low Priority)*
-------------------------------------------

* Bundle `python-magic` dependencies?
  https://github.com/ahupp/python-magic#dependencies
