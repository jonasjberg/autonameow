`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  
University mail: `js224eh[a]student.lnu.se`  

--------------------------------------------------------------------------------

`autonameow` TODO-list
======================


High Priority
-------------

* `[TD0167]` Cleanup data storage in the `Repository`.

* `[TD0166]` The analyzers should be able to set probabilities on the fly.

* `[TD0165]` Integrate the `DataBundle` class completely.

* `[TD0157]` __Look into the analyzers `FIELD_LOOKUP` attribute.__  
    Does it make sense to keep this? Differences between "analyzers" and
    "extractor" enough to motivate them continue being separate concepts?
    Only the `FilenameAnalyzer` currently has a `FIELD_LOOKUP` (!)

* `[TD0146]` Rework "generic fields", possibly collecting fields in "records".

* `[TD0142]` __Rework overall architecture to fetch only explicitly needed data.__  
  Refer to `notes/architecture.md` for details.

* `[TD0131]` __Limit `Repository` memory usage__  
  Given enough files, it currently eats up all the RAM, which causes other
  parts of the program to fail, especially launching subprocesses.

* `[TD0115]` __Clear up uncertainties about data multiplicities.__  
  I.E. list of data dicts vs. single data dict that contains a list
  of data (`multivalued: True`).

* `[TD0100]` Spec out "operating modes" and functionality requirements.

* `[TD0099]` Use `python-prompt-toolkit` for the interactive cli UI.

* `[TD0089]` Validate only "generic" data fields when reading config.

* `[TD0102]` Fix inconsistencies in results passed back by analyzers.

* `[TD0108]` Fix inconsistencies in results passed back by plugins.

* `[TD0126]` Clean up boundaries/interface to the `analyzers` package.

* `[TD0128]` Clean up boundaries/interface to the `plugins` package.

* `[TD0129]` Enforce passing validated data to `NameTemplateField.format()`.

* `[TD0138]` __Fix inconsistent type of `RuleCondition.expression`.__  
  Probably best to always store a list of expressions, even when there is only one.
  Alternatively, implement separate abstraction of an "expression".


Medium Priority
---------------

* `[TD0168]` Remove or re-implement the `TextAnalyzer`.

* `[TD0161]` Handle mapping/translation between "generic"/specific MeowURIs.

* `[TD0158]` Evaluate regression test assertions of "skipped renames".

* `[TD0151]` __Fix inconsistent use of classes vs. class instances.__  
    Attributes of the provider classes are accessed both from uninstantiated
    classes and class instances. The `metainfo()` method should be accessible
    without first having to instantiate the class.

* `[TD0137]` __Add rule-specific replacements.__  
    Maybe have the current replacements apply globally, as in that they are
    always used as a final step in preparing the file name.
    It might be useful to also allow specifying rule-specific replacements
    that are used only if the containing rule is chosen.

    Example of current configuration replacements;

    ```yaml
    POST_PROCESSING:
        replacements:
            -{3,}: '--'
            \.{2,}: '.'
            _{2,}: '_'
    ```

    Possible rule-specific replacements:

    ```yaml
    Quicktime Desktop Recording:
        CONDITIONS:
            extractor.filesystem.xplat.basename.full: 'Untitled.mov'
            extractor.filesystem.xplat.contents.mime_type: 'video/quicktime'
            extractor.filesystem.xplat.pathname.full: '/Users/jonas/Desktop'
        NAME_TEMPLATE: '{datetime} -- screenshot macbookpro.mov'
        DATA_SOURCES:
            datetime: extractor.metadata.exiftool.QuickTime:CreationDate
        exact_match: false
        ranking_bias: 0.9
        POST_PROCESSING:
            replacements:
                (bar){2,}: bar
                foo: Gibson Rules
    ```

* `[TD0136]` Look into "requesting" already available data.

* `[TD0134]` Consolidate splitting up text into "chunks".

* `[TD0132]` Improve blacklisting data, prevent repeated bad requests to APIs.

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

* `[TD0054]` __Represent datetime as UTC within autonameow.__  
  Convert incoming time to UTC and convert to local time as a final step before
  presentation or use.

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

* `[TD0164]` Mitigate mismatched throwing/catching of exceptions.

* `[TD0163]` __Fix premature importing of providers.__  
    Running `autonameow --help` if some provider dependency is missing should
    not print `Excluding analyzer "<class 'analyze_ebook.EbookAnalyzer'>" due
    to unmet dependencies` as the first thing, above the actual help text.
    Instead "load" providers and check these dependencies just prior to
    actually using them.

* `[TD0162]` __Split up `autonameow.yaml` into separate files.__  
    Use separate configuration files for options, rules, etc.

* `[TD0160]` Consolidate setting up working directories that might not exist.

* `[TD0159]` Fix stand-alone extractor not respecting the `--quiet` option.

* `[TD0154]` __Add "incrementing counter" placeholder field__  
    Add name template placeholder field for different kinds of numbering, I.E.
    a name template like `foo_{counter}.{ext}` gives `foo_001.c`, `foo_002.c`.

    * Only used in case of conflicts?
    * Used all the time? Used only if `conditions`?
    * Options for formatting? Fixed widths, zero-padding, etc.
    * Global options? Per-instance (config rule?) options?

* `[TD0153]` __Detect and clean up incrementally numbered files__  
    Add features for cleaning up inconsistent numbering.

    * Change existing numbers *("renumbering"?)*

        ```
        booklet.jpg   ->  booklet1.jpg
        booklet1.jpg  ->  booklet2.jpg
        booklet2.jpg  ->  booklet3.jpg
        ```

    * __Fix inconsistent padding__

        ```
        1.c    ->  01.c
        002.c  ->  02.c
        3.c    ->  03.c
        10.c   ->  10.c
        ```
        Globally defined width applies everywhere or adjust dynamically to fit?

    * __Fix somewhat common case of Windows Explorer batch__

        ```
        foo (10).TXT  ->  foo (10).TXT
        foo (1).TXT   ->  foo (01).TXT
        foo (2).TXT   ->  foo (02).TXT
        foo.TXT       ->  foo.TXT
        ```

* `[TD0152]` __Fix invalid name template field replacements.__  
    Replacements in the `Publisher` class in `fields.py` are always applied if
    any substring matches, which might cause undesired results.  Might be
    better to stop after the first replacement has been applied, or do the
    replacements ordered by the number of matched characters to be replaced.

* `[TD0149]` Handle exceptions raised in `evaluate_boolean_operation()`.

* `[TD0148]` Fix `!!python/object` in `--dump-config` output.

* `[TD0145]` Add script for automating release of a new version.

* `[TD0144]` Avoid enforcing/pruning cache file size too frequently.

* `[TD0143]` __Add option to execute "hooks" at certain events.__  
    Allow specifying executing arbitrary commands when specific events occur.
    One use-case example is moving successfully renamed files to another
    directory.

* `[TD0141]` Coerce raw values to known types in the `ConfigurationParser`.

* `[TD0140]` Template field classes `str()` method not working as intended.

* `[TD0139]` Warn if data sources does not match name template placeholders?

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

* `[TD0130]` __Implement general-purpose matching/extraction of substrings.__  
    Primary purpose is to provide matching and also removal of matched parts.

    For instance, given a full string like `Skill: 1337 Meow - foo`,  searching
    for "skills" with regex `r'[sS]kill: ?(\d)+'`, the matched part should be
    returned and also removed from the original string. Alternatively, the match
    results would contain information on where in the original string that the
    match was found.

    This is a non-issue when using only regexes to do the substring searches,
    but if the search is performed with a function call, removing the matched
    substring becomes a bit messy.

    Related to `[TD0020]`. This functionality is provided by `guessit`!

* `[TD0121]` Create a script for generating regression tests.

* `[TD0118]` Improve robustness and refactor searching text for editions.

* `[TD0114]` Improve the `EbookAnalyzer`.

* `[TD0113]` Fix exceptions not being handled properly (?)

* `[TD0109]` __Allow arbitrary name template placeholder fields.__  
    It is currently difficult to use a rule similar to this:

    ```yaml
    TV-series:
        CONDITIONS:
            extractor.filesystem.xplat.pathname.full: '/tank/media/tvseries'
            extractor.filesystem.xplat.contents.mime_type: video/*
        NAME_TEMPLATE: '{title} S{season}E{episode}.{extension}'
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

* `[TD0096]` Fix some replacements cause incorrect color highlighting.

* `[TD0091]` Take a look at old code in `util/dateandtime.py`.

* `[TD0068]` Let the user specify which languages to use for OCR.

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

    Prevent this from happening;
    ```
    Candidates for unresolved field: title

    #   SOURCE                     PROBABILITY  FORMATTED VALUE
    =   ======                     ===========  ===============
    0   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    1   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    2   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    3   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    4   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    5   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    6   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    7   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    8   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    9   (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    10  (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    11  (unknown source)           1.0          "Syntax Warning: Invalid Font Weight"
    ```

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
  In relation to future weighting and prioritizing of analysis results.

* `[TD0094]` __Search text for DOIs and query external services__  
  Similar to ISBN-numbers. Could be used as primary identifier/key in records
  and to query external services for publication metadata.
  Example DOI: `10.1109/TPDS.2010.125`.


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

* Graphical User Interface of some kind, as an alternative to the command-line.


Windows-compatibility *(Very Low Priority)*
-------------------------------------------

* Bundle `python-magic` dependencies?
  https://github.com/ahupp/python-magic#dependencies
