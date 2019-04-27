`autonameow`
============
Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------

`autonameow` TODO-list
======================


High Priority
-------------

* `[TD0202]` __Handle signals and graceful shutdown properly!__

* `[TD0198]` __Separate repositories for "provider" and "internal" data__  
    One repository would store data for URIs like
    `extractor.metadata.exiftool.PDF:Author` and "aliased leaf" URIs like
    `extractor.metadata.exiftool.author`.
    This would be the raw unprocessed data, straight from the `exiftool`
    provider.

    Another repository stores data, for URIs like `generic.metadata.author`.
    Data returned from this repository will have been processed, cleaned,
    "unpacked", etc.
    This allows lazily processing data as required, serves to clean up the
    current repository implementation, as well as helping separation of data
    processing and allows accessing the various forms the data at various
    stage.

* `[TD0187]` __Fix "clobbering" of analyzer results..__

* `[TD0185]` __Rework the highest level data request handler interface.__

    * Don't pass the `master_provider` as a module. Use new "controller" class?
    * Fix both global and direct references used to access the `Registry` and
      `master_provider` functions.  
      Some places access module-level functions directly after importing the
      module, while some get a reference to the module passed in as an argument
      (emanating from `Autonameow.master_provider`. Incomplete and forgotten?)

    * Look at possibly wrapping up the pairs of "runner" and "registry" classes
      in a "facade"-like controller class. Alternatively, just try to clean up
      the current messy accessing.
      Related notes:  `notes/2018-03-24-rough-architecture-sketch.jpg`

    * Allow setting up (instantiating) provider classes once, then re-use the
      instances when processing files.
      Related to `[TD0183]` on using one `exiftool` process in "batch mode".

* `[TD0175]` __Handle requesting exactly one or multiple alternatives.__  
    The current high-level interface for fetching data might return a single
    piece of data or many alternatives. This means that "clients" have to
    perform various checks and either fail if they are unable to figure out
    *which alternative to use* or attempt to pick out the "best" alternative.

    One possible solution is to replace the single function `request()`
    with something like `request_one()` and `request_all()`.

    Another solution is to pass some kind of qualifier with each query.
    Or possibly a "tie-breaker" callback or object that can be evaluated to
    resolve cases where a single piece of data is needed but the request
    results in several candidates.

* `[TD0171]` __Separate all logic from the user interface.__  
    Avoid using "global" input/output functionality directly.

* `[TD0167]` Cleanup data storage in the `Repository`.

* `[TD0166]` The analyzers should be able to set field map weights on the fly.

* `[TD0157]` __Look into the analyzers `FIELD_LOOKUP` attribute.__  
    Does it make sense to keep this? Differences between "analyzers" and
    "extractor" enough to motivate them continue being separate concepts?
    Only the `FilenameAnalyzer` currently has a `FIELD_LOOKUP` (!)

* `[TD0146]` Rework "generic fields", possibly collecting fields in "records".

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

* `[TD0126]` Clean up boundaries/interface to the `analyzers` package.

* `[TD0129]` Enforce passing validated data to `NameTemplateField.format()`.

* `[TD0138]` __Fix inconsistent type of `RuleCondition.expression`.__  
  Probably best to always store a list of expressions, even when there is only one.
  Alternatively, implement separate abstraction of an "expression".


Medium Priority
---------------

* `[TD0201]` __Implement "unpacking" field values__  
    Add proper system to detect and process field values that actually contain
    multiple separate values potentially belonging to different fields.

    Example:
    ```
      URI:  Ebook Metadata Title
    VALUE:  'Practical Kibble Sight With CatVision / Gibson Sjöberg, ... [Et Al.]'
    Should unpack to unpacked = {
        'author': 'Gibson Sjöberg',
        'title': 'Practical Kibble Sight With CatVision',
    }
    ```

* `[TD0200]` __Improve system for finding probable file extensions.__  
    The system for finding a "probable" extension should accept additional
    input data in order to make better decisions about certain files.
    For instance, all files named `METADATA`, with MIME-types `text/*`
    should probably return an empty extension as the most probable.

    This requires at least passing in the "basename prefix" to the
    `likely_extension()` function in `analyze_filename.py`.
    But things like the parent directory name should also prove useful
    in order to produce better results.

* `[TD0196]` Allow user to define maximum lengths for new names.

* `[TD0197]` Template field-specific length limits and trimming.  
    When populating the final name, check the total length of the final new
    file name. If the total length of the file name exceeds a user-defined max
    length or if any of the individual placeholder fields exceed their specific
    max lengths, trim field lengths until the individual field limits are no
    longer exceeded.

    If the total length of the new name still exceeds the total length limit,
    trim individual fields in some yet unknown way.

    If the name template is `{title} {subtitle}`, possibly trim or remove the
    subtitle, etc. This behaviour should be made field- and/or data-specific.

    Related to TODO `[TD0196]` on allowing user-defined max length.

* `[TD0190]` __Join/merge metadata "records" with missing field values__  
    When de-duplicating and discarding "duplicate" sets of metadata
    ("records"), check if the chosen metadata record has any missing or empty
    field values that are present in the other metadata record.  If so, "join"
    fields with missing values before discarding the "duplicate" record.

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
            extractor.filesystem.xplat.basename_full: 'Untitled.mov'
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

* `[TD0015]` Allow conditionals in the configuration rules.
    * Test if a rule is applicable by evaluating conditionals.
        * Textual contents of the file matches a regular expression?
        * Some date/time-information lies within some specific range.

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
    * __This is a non-trivial problem__, I would rather not re-implement
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

* `[TD0195]` __Handle malformed metadata with duplicated authors__  
    Detect and filter duplicated authors like `['Gibson Sjöberg', 'Gibson']`

* `[TD0194]` __Handle pdfs without "overlay" text__  
    Detect when pdf documents do not contain any text that can be extracted
    with `pdftotext` and run do OCR text extraction instead.
    Each page of the PDF document must first be converted to some suitable
    image format that can be passed on to OCR text extraction.

* `[TD0193]` __Clean up arguments passed to `FilesystemError`__  
    Fix inconsistent usage of the `FilesystemError` exception class.

    Two calls in `util/disk/yaml.py` pass additional information;
    ```python
    raise FilesystemError(dest_filepath, e)
    ```

    While other calls look like;
    ```python
    try:
        foo()
    except FooError as e:
        raise FilesystemError(e)
    ```

    Might be worthwhile to add class attribute constants.
    So that something like;
    ```python
    raise FilesystemError(dest_filepath, 'Insufficient permissions')
    ```

    Would become something more along the lines of;
    ```python
    raise FilesystemError(dest_filepath, FilesystemError.ERROR_PERMISSION)
    ```

* `[TD0192]` __Detect and extract editions from titles__  
    This is already done in the `EbookAnalyzer` using functions in
    `patternmatching.py` but this needs to be extracted into a separate system.

    The resulting data might also include a confidence level; given a title
    like `Head First autonameow`, the substring `First` might be assumed to be
    an edition but it might also just be part of the title. So the resulting
    data returned by the system could assign a low confidence level to the
    transformation;

    ```python
    >>> yet_unimplemented_system('Head First autonameow')
    {'edition': 1, 'confidence': 0.1, 'title': 'Head autonameow'}
    ```

* `[TD0191]` __Detect and extract subtitles from titles__  
    ISBN metadata currently often contains titles on the form
    `X Essentials - [Programming the X Framework]` and
    `X Essentials - Programming the X Framework`.

    This should be detected and split up into two parts, so that the `title`
    field becomes `X Essentials` and a new `subtitle` field would get
    `Programming the X Framework`.

    This would include adding a new `subtitle` name template placeholder as
    well as other representations like a "generic" field, etc.

    If the concept of metadata "records" is to be used, this step of detecting
    fields within fields should probably be done before storing results in the
    repository somewhere when individual provider data are "wrapped"? *(?)*

* `[TD0186]` Re-implement the `EpubMetadataExtractor`.

* `[TD0184]` Clean up translation of `metainfo` to "internal format".

* `[TD0181]` Use machine learning in ISBN metadata de-duplication.

* `[TD0177]` __Refactor the `ConfigFieldParser` classes.__  
    Should not handle both parsing and evaluation of expressions.
    This will have to be done in conjunction with `[TD0015]`.
    Also, see related item `[TD0138]`.

* `[TD0173]` Use `pandoc` to extract information from documents.

* `[TD0164]` Mitigate mismatched throwing/catching of exceptions.

* `[TD0162]` __Split up `autonameow.yaml` into separate files.__  
    Use separate configuration files for options, rules, etc.

* `[TD0160]` Consolidate setting up working directories that might not exist.

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

* `[TD0149]` Handle exceptions raised in `evaluate_boolean_operation()`.

* `[TD0148]` Fix `!!python/object` in `--dump-config` output.

* `[TD0145]` Add script for automating release of a new version.

* `[TD0144]` Avoid enforcing/pruning cache file size too frequently.

* `[TD0143]` __Add option to execute "hooks" at certain events.__  
    Allow specifying executing arbitrary commands when specific events occur.
    One use-case example is moving successfully renamed files to another
    directory.

* `[TD0141]` Coerce raw values to known types in the `ConfigurationParser`.

* `[TD0139]` Warn if data sources does not match name template placeholders?

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

* `[TD0109]` __Allow arbitrary name template placeholder fields.__  
    It is currently difficult to use a rule similar to this:

    ```yaml
    TV-series:
        CONDITIONS:
            extractor.filesystem.xplat.pathname.full: '/tank/media/tvseries'
            extractor.filesystem.xplat.contents.mime_type: video/*
        NAME_TEMPLATE: '{title} S{season}E{episode}.{extension}'
        DATA_SOURCES:
            title: extractor.filesystem.guessit.title
            season: extractor.filesystem.guessit.season
            episode: extractor.filesystem.guessit.episode
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

* `[TD0068]` Let the user specify which languages to use for OCR.

* `[TD0026]` Implement safe handling of symbolic link input paths.

* __Add additional filetype-specific "extractors"__
    * `[TD0027]` __Word Documents__
        * Extract plain text and metadata from Word documents.
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
    * Some providers return *a lot* of tags, too many to use in a filename
      without any kind or probably multiple selection processes.
    * It would be very useful to be able to filter tags by getting the
      intersection of the unfiltered tags and a whitelist.
    * Allow specifying allowed tags in the configuration?
    * Allow specifying mutually exclusive tags in the configuration?
    * Convert various metadata to tags.
      From `XMP:Description: Computers, Software, Engineering` to a list of
      tags `computers`, `software` and `engineering`.


* `[TD0040]` Add assigning tags to GPS coordinates for tagging images with EXIF
  GPS data. Look into comparing coordinates with the
  [Haversine formula](http://en.wikipedia.org/wiki/Haversine_formula).

* `[TD0043]` Allow the user to tweak hardcoded settings using the
  configuration.

* `[TD0045]` Add ability to rename directories.

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

* `[TD0199]` Bundle `python-magic` dependencies?
    https://github.com/ahupp/python-magic#dependencies
