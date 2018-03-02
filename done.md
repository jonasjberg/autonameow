`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  
University mail: `js224eh[a]student.lnu.se`  

--------------------------------------------------------------------------------

Completed TODO-list Entries
===========================

### 2018-03-02

> Medium Priority
> ---------------
>
> * `[TD0178]` __Store only strings in `FIELD_LOOKUP`.__  
>     Further decouples the extractors from the rest of the system.
>     Would also allow potentially storing the `FIELD_LOOKUP` in a separate file
>     that is loaded at run-time.
>
> Low Priority
> ------------
>
> * `[TD0163]` __Fix premature importing of providers.__  
>     Running `autonameow --help` if some provider dependency is missing should
>     not print `Excluding analyzer "<class 'analyze_ebook.EbookAnalyzer'>" due
>     to unmet dependencies` as the first thing, above the actual help text.
>     Instead "load" providers and check these dependencies just prior to
>     actually using them.

### 2018-02-27

> Low Priority
> ------------
>
> * `[TD0096]` Fix some replacements cause incorrect color highlighting.

### 2018-02-24

> High Priority
> -------------
>
> * `[TD0108]` Fix inconsistencies in results passed back by plugins.
>
> * `[TD0128]` Clean up boundaries/interface to the `plugins` package.
>
> Medium Priority
> ---------------
>
> * `[TD0009]` Implement proper plugin interface
>     * Have plugins "register" themselves to a plugin handler?
>     * Querying plugins might need some translation layer between the
>       `autonameow` field naming convention and the specific plugins naming
>       convention. For instance, querying a plugin for `title` might require
>       actually querying the plugin for `document:title` or similar.
>     * Abstract base class for all plugins;
>         * Means of providing input data to the plugin.
>         * Means of executing the plugin.
>         * Means of querying for all or a specific field.

### 2018-02-23

> High Priority
> -------------
>
> * `[TD0176]` __Fix inconsistent `CrossPlatformFileSystemExtractor` leaves__  
>     All provider MeowURIs consist of 4 parts except for one extractor.
>     Handling the case where a leaf can consist of multiple parts requires
>     better parsing of strings and lots of special cases and it might never
>     actually be desired.  Even though it might be nice to support this case,
>     it currently makes much more sense to fix this inconsistency.
>
> Low Priority
> ------------
>
> * `[TD0113]` Fix exceptions not being handled properly (?)

### 2018-02-19

> Medium Priority
> ---------------
>
> * `[TD0136]` Look into "requesting" already available data.
>
> * `[TD0169]` Remove or re-implement the `ImageAnalyzer`.
>
> * `[TD0168]` Remove or re-implement the `TextAnalyzer`.
>
> * `[TD0028]` __E-books epub/mobi__
>     * Extract metadata fields. Look into using `calibre`.

### 2018-02-15

> High Priority
> -------------
>
> * `[TD0170]` Use mock `ui` in regression test `AutonameowWrapper`.

### 2018-02-13

> High Priority
> -------------
>
> * `[TD0165]` Integrate the `DataBundle` class completely.
>
> * `[TD0142]` __Rework overall architecture to fetch only explicitly needed data.__  
>   Refer to `notes/architecture.md` for details.
>
> Medium Priority
> ---------------
>
> * `[TD0019]` Rework the `FilenameAnalyzer`

### 2018-02-08

> High Priority
> -------------
>
> * `[TD0156]` __Set up Unicode string encoding boundary in `ui`.__  
>     Enforce passing only Unicode strings to the `ui` module.

### 2018-02-07

> High Priority
> -------------
>
> * `[TD0150]` Map "generic" MeowURIs to (possible) provider classes.

### 2018-02-03

> High Priority
> -------------
>
> * `[TD0127]` Clean up boundaries/interface to the `extractors` package.
>
> * `[TD0133]` Fix inconsistent use of MeowURIs; `MeowURI` instances and strings.

### 2018-01-18

> High Priority
> -------------
>
> * `[TD0155]` Implement `--timid` mode.

### 2018-01-16

> High Priority
> -------------
>
> * `[TD0147]` Fix `providers_for_meowuri()` stops searching after first match.

### 2017-12-16

> Low Priority
> ------------
>
> * `[TD0101]` __Add ability to limit sizes of persistent storage/caches.__  
>   Store timestamps with stored data and remove oldest entries when exceeding
>   the file size limit.

### 2017-12-13

> Low Priority
> ------------
>
> * `[TD0135]` __Add option to display rule matching information.__  
>     Provide additional information on which rule conditions failed/passed
>     evaluation. Running in verbose mode currently shows the following;
>     ```
>     [INFO] Remaining, prioritized rules:
>     [INFO] Rule #1 (Exact: No   Score: 1.00  Weight: 0.25  Bias: 0.01) Extension from MIME-type
>     [INFO] Rule #2 (Exact: No   Score: 0.33  Weight: 0.75  Bias: 0.80) Dropbox Camera Uploads Images screenshots
>     [INFO] Rule #3 (Exact: No   Score: 0.25  Weight: 1.00  Bias: 0.80) Dropbox Camera Uploads Images named as per filetags convention
>     [INFO] Rule #4 (Exact: No   Score: 0.00  Weight: 0.75  Bias: 0.90) Quicktime Desktop Recording
>     [INFO] Discarded rules:
>     [INFO] Rule #1 (Exact: Yes  Score: N/A   Weight: N/A   Bias: 1.00) DCIMs in HOME/Pictures/incoming
>     [INFO] Rule #2 (Exact: Yes  Score: N/A   Weight: N/A   Bias: 0.80) Dropbox Camera Uploads Images
>     [INFO] Rule #3 (Exact: Yes  Score: N/A   Weight: N/A   Bias: 0.90) Unsorted Ebooks
>     [INFO] Rule #4 (Exact: Yes  Score: N/A   Weight: N/A   Bias: 0.70) Unsorted Ebooks without edition
>     [INFO] Rule #5 (Exact: Yes  Score: N/A   Weight: N/A   Bias: 0.10) Might be Ebooks
>     [INFO] Rule #6 (Exact: Yes  Score: N/A   Weight: N/A   Bias: 1.00) IMG_s in HOME/Pictures/incoming
>     [INFO] Rule #7 (Exact: Yes  Score: N/A   Weight: N/A   Bias: 0.10) Fix extension of jpeg images
>     [INFO] Using rule: "Extension from MIME-type"
>     [INFO] New name: "IMG_20170829_083638.jpg"
>     ```
>     Information on *which rule conditions* that caused a rule to be discarded
>     is currently only available in the debug mode output.
>
>     It would be useful to add an option to display information on the rule
>     matching, to aid in writing new rules.

### 2017-12-11

> Medium Priority
> ---------------
>
> * `[TD0014]` Possibly redesign high-level handling of a "configuration".
>     * Decouple the `Configuration` instance from I/O.
>     * Think about separating validation and parsing of incoming
>       configuration data from the `Configuration` class.

### 2017-12-01

> Low Priority
> ------------
>
> * `[TD0011]` Think about how the overall "analysis" might be executed more than
>   once.
>     * Results from an initial analysis might be passed to the second analysis.
>     * If a matched and active rule does not specify all required sources; the
>       missing sources might be filled in by a more targeted approach using data
>       gathered during the first run.

### 2017-11-29

> High Priority
> -------------
>
> * `[TD0066]` __Fix bad encoding of bytestring paths when listing results.__  
>   When listing results with any of the `--list-*` options, paths are not
>   displayed properly due to them not being handled properly before being passed
>   to `yaml.dump` which performs the formatting of the results dict.

### 2017-11-28

> Low Priority
> ------------
>
> * `[TD0059]` Replace `--list-datetime`, `--list-title` and `--list-all`
>   with something more flexible like `--list {FIELD}`.
>
> * `[TD0124]` Add option (script?) to run failed regression tests manually.

### 2017-11-24

> High Priority
> -------------
>
> * `[TD0084]` Add handling collections (lists, etc) to the type wrapper classes.

### 2017-11-21

> Low Priority
> ------------
>
> * `[TD0123]` Add option (script?) to re-run failed regression tests.

### 2017-11-19

> High Priority
> -------------
>
> * `[TD0106]` Fix inconsistencies in results passed back by extractors.

### 2017-11-17

> High Priority
> -------------
>
> * `[TD0088]` Handle case where `ExtractedData.wrapper` is `None`.
>
> * `[TD0082]` Integrate the `ExtractedData` class.
>
> * `[TD0087]` Clean up messy and sometimes duplicated wrapping of "raw" data.
>
> * `[TD0119]` Separate adding contextual information from type coercion.
>
> Medium Priority
> ---------------
>
> * `[TD0041]` Improve data filtering prior to name assembly in `NameBuilder`
>
> Low Priority
> ------------
>
> * `[TD0033]` Refactor unit tests.
>     * Mitigate superlinear increase in unit test execution speed.
>     * Try to rewrite tests that operate on actual files
>         * Cache results from expensive calls, avoid repeated actions.
>         * Substitute I/O-operations with some kind of mocking.

### 2017-11-10

> High Priority
> -------------
>
> * `[TD0122]` __Move away from using callbacks to return analyzer results.__  
>   Using callbacks to pass data back from the analyzers do not currently
>   provide any benefits but is a lot more difficult to read and test than
>   just simply returning the data directly, as the extractors do.
>
> Low Priority
> ------------
>
> * `[TD0120]` Use less verbose default output in the regression test runner.

### 2017-11-07

> High Priority
> -------------
>
> * `[TD0117]` Implement automated regression testing.

### 2017-10-29

> Medium Priority
> ---------------
>
> * `[TD0116]` Remove persistent caching in the text extractors.

### 2017-10-21

> High Priority
> -------------
>
> * `[TD0105]` Integrate the `MeowURI` class.

### 2017-10-11

> Medium Priority
> ---------------
>
> * `[TD0017]` Rethink how specified sources are connected to actual sources.
>   Take for example the configuration rule:
>
>     ```yaml
>     RULES:
>     -   CONDITIONS:
>             contents:
>                 mime_type: image/*
>             filesystem:
>                 pathname: ~/Dropbox/Camera Uploads/.*
>         DATA_SOURCES:
>             extension: contents.mime_type
>     ```
>   This will fail, or *should fail* as MIME types on the form `image/jpeg`,
>   `image/png`, etc can't be used as a file extension without some
>   pre-processing -- converting `image/png` to `png`.
>
> Low Priority
> ------------
>
> * `[TD0039]` Do not include the rule attribute `score` when listing the
>   configuration with `--dump-config`.
>
> * `[TD0038]` Add new name format placeholder field `{year}`.

### 2017-10-10

> Low Priority
> ------------
>
> * `[TD0097]` Improve and fully implement caching to files on disk.

### 2017-10-07

> Medium Priority
> ---------------
>
> * `[TD0098]` Use checksums as keys for cached data, not paths.

### 2017-10-06

> Medium Priority
> ---------------
>
> * `[TD0103]` Handle duplicate metadata results from different ISBNs.

### 2017-10-05

> High Priority
> -------------
>
> * `[TD0044]` __Rework converting "raw data" to internal representations__
>     * Converting raw data to internal representations is currently implemented
>       very poorly and must be reworked.
>     * Think about how to handle translation in the "general" sense; high-level,
>       abstract. Would it be wise to let data extractors convert raw data to
>       internal types? (For example; messy OCR text to `datetime` object)
>         * A "general solution" using some new entity tasked with translating
>           data *might be too "general"* considering the likely granularity of
>           operations needed to perform the conversion.  That is, if the
>           required operations differs greatly between data sources, abstracting
>           the process would mostly add yet another layer of indirection ..
>     * Think about how wrapped data types (`[TD0002]`) relates to this.
>
> Medium Priority
> ---------------
>
> * `[TD0070]` Implement arbitrary common personal use case.

### 2017-09-29

> High Priority
> -------------
>
> * `[TD0012]` Add some type of caching.
>     * Extracting text from a PDF should only have to happen once, at most.
>       Preferably not at all, unless a rule conditional tests the text content
>       or the text is needed elsewhere.
>     * Image OCR is very slow, should only be executed when needed, caching the
>       results for all accesses.
>
> Medium Priority
> ---------------
>
> * `[TD0023]` Add additional option to force non-interactive mode (`--batch`?)
>
> Low Priority
> ------------
>
> * `[TD0042]` Respect the `--quiet` option. Suppress (all but critical?) output.

### 2017-09-28

> High Priority
> -------------
>
> * `[TD0090]` Complete initial implementation of "generic" data fields.

### 2017-09-27

> High Priority
> -------------
>
> * `[TD0004]` __Text encoding issues__
>     * Enforce strict boundaries between all external systems and an internal
>       text data representation.
>     * Store original filename parts as both bytestrings and the internal
>       representation?  If the user wants to use a part of the original file
>       name in the result, the conversion can not be lossy. Best way to prevent
>       issues is to store bytestrings and perform any processing on copies that
>       have __not__ been converted to the internal format?
>
> Medium Priority
> ---------------
>
> * `[TD0062]` Look at testing that all name template fields are mapped to data
>   sources. This could be done when reading the configuration, instead of later
>   on in the name builder.
>
> * `[TD0049]` __Think about defining legal "placeholder fields".__
>   Might be helpful to define all legal fields (such as `title`, `datetime`,
>   `author`, etc.) somewhere and keep references to type coercion wrappers,
>   maybe validation and/or formatting functionality; in the field definitions.
>
> * `[TD0018]` There are more cases like the above that should be thought about.
>   A common case is the slight modification to the current file name.
>   Original file name:
>     ```
>     2017-06-20_00-49-56 Working on autonameow.png
>     ```
>   Desired file name:
>     ```
>     2017-06-20T004956 Working on autonameow.png
>     ```
>   How should this be specified in the configuration?
>   A simple alternative is to specify the filename analyzer as the source.
>   The `DATETIME_FORMAT` makes sure that the timestamp format is changed.
>
>     ```yaml
>     RULES:
>     -   DATA_SOURCES:
>             extension: contents.basename.extension
>             datetime: analysis.filename.{?????}
>             title: filesystem.basename.prefix
>         NAME_FORMAT: "{datetime} {title}.{extension}"
>     DATETIME_FORMAT:
>         datetime: '%Y-%m-%dT%H%M%S'
>     ```
>   But this is not configurable -- how would the filename analyzer know
>   which of many possible datetime results to use?

### 2017-09-25

> Low Priority
> ------------
>
> * `[TD0086]` __Use one `SessionRepository` per `Autonameow` instance.__  
>   The `Autonameow` class "manages a running instance of the program" should
>   have its own instance of the `Repository` class. This is fine for now but
>   should be fixed to avoid confusion and future problems.

### 2017-09-22

> Low Priority
> ------------
>
> * `[TD0081]` Bundle the `pyexiftool` dependency. Add to `autonameow/thirdparty`.

### 2017-09-20

> Medium Priority
> ---------------
>
> * `[TD0093]` Implement using config `POST_REPLACEMENTS` in name builder.

### 2017-09-17

> Medium Priority
> ---------------
>
> * `[TD0083]` __Clean up the type wrapper classes.__  
>     * Remove ambiguities around returning "NULL" and raising `AWTypeError`.
>     * Clean up the "interface" to the type wrappers. If callers only use the
>       shared singleton module attributes, I.E. all data flows in through
>       `__call__`, then unit testing the `coerce` method is superfluous.
>     * Look at the `normalize` methods, think about removing them if they
>       continue to go unused.  See also, related entry: `[TD0060]`

### 2017-09-14

> Low Priority
> ------------
>
> * `[TD0060]` Implement or remove the type wrapper classes `format` method.

### 2017-09-11

> Medium Priority
> ---------------
>
> * `[TD0085]` Simplify extractor discovery and import. Use only packages?

### 2017-09-10

> High Priority
> -------------
>
> * `[TD0061]` Re-implement basic queries to the "microsoft vision" plugin.

### 2017-09-08

> Low Priority
> ------------
>
> * __Add additional plugins__
>     * `[TD0030]` Plugin for querying APIs with ISBN numbers.
>       (Already implemented in `autoname_pdf.py` and `isbn_query.py`)

### 2017-08-25

> High Priority
> -------------
>
> * `[TD0080]` __Fix literal strings not considered a valid "data source".__  
>   It is currently not possible to specify a fixed literal value for a name
>   template field. Take the following example rule;
>
>     ```yaml
>   -   CONDITIONS:
>             filesystem.basename.full: 'P[0-9]{7}.JPG'
>             filesystem.contents.mime_type: image/jpeg
>         DATA_SOURCES:
>             datetime: metadata.exiftool.EXIF:DateTimeOriginal
>             extension: jpg
>         NAME_FORMAT: '{datetime}.{extension}'
>     ```
>
>   This rule will not pass validation because the literal string `jpg` is
>   discarded by the `is_valid_source` function in `core/config/rules.py`;
>
>   ```
>   $ autonameow --debug --dry-run --automagic P1020738.JPG 2>&1 | grep -i invalid
>   [DEBUG] parse_data_sources (549) Invalid data source: [extension]: jpg
>   ```
>
>   __Related:__ `[TD0015][TD0017][TD0049]`

### 2017-08-23

> High Priority
> -------------
>
> * `[TD0076]` __Have all non-core components register themselves at startup.__  
>   A lot of the problems with implementing a plugin-interface, handling queries
>   from components to a centralized "data pool", only running the required
>   plugins/extractors/analyzers for performance, etc; might possibly be solved
>   by implementing a more sophisticated method of keeping track of available
>   components.
>     * Enumerate all available extractors, analyzers and plugins at startup.
>         * Check that dependencies are available; external executables, etc.
>         * Have the components "register" their "meowURIs". If the component
>           could return data with "meowURI"
>           `metadata.exiftool.PDF:CreateDate`, register the first part:
>           `metadata.exiftool`.
>     * Read the configuration file and get a list of all referenced "meowURIs".
>     * Find out which components could produce the referenced "meowURIs" and
>       use this information to selectively run only components that are
>       required.
>
> Medium Priority
> ---------------
>
> * `[TD0056]` __Determine which extractors should be used for each input.__  
>   In order to add conditional data extraction, a list of relevant extractors
>   must be produced for each input path that will be processed. This should
>   probably be collected during configuration parsing and rule matching; if a
>   rule needs some information to be evaluated, the relevant extractor must
>   be enqueued and executed.
>
> * `[TD0057]` __Look at the optional `field` parameter of the `query` method.__  
>   The extractor classes `query` method takes an optional parameter `field` that
>   seems to be unused. Some classes, like the text extractors will probably not
>   return anything but text. Look into possibly removing the optional argument
>   or rework how the extractor classes are queried.

### 2017-08-22

> Medium Priority
> ---------------
>
> * `[TD0071]` Move file name "sanitation" to the `NameBuilder` or elsewhere.
>
> * `[TD0078]` Check extractor dependencies when enumerating extractor classes.


### 2017-08-21

> Medium Priority
> ---------------
>
> * `[TD0079]` __Refactor validation of `Rule` data.__  
>   Probably more sense to perform validation of the data used to construct
>   `Rule` instances in the `Rule` class instead of scattered around
>   functions in the `configuration` module and the `Configuration` class.

### 2017-08-17

> High Priority
> -------------
>
> * `[TD0063]` Fix crash when a data source is mapped but data itself is missing.

### 2017-08-17

> High Priority
> -------------
>
> * `[TD0073]` __Fix or remove the `SessionDataPool` class.__
>
> * `[TD0077]` __Implement a "repository" to handle "query string" queries__
>
> * `[TD0069]` Calculate file rule scores as `score = conditions_met /
>   number_of_conditions`, I.E. use normalized floats.
>
> Medium Priority
> ---------------
>
> * `[TD0052]` Analyzer classes should provide their respective "query strings"

### 2017-08-16

> Medium Priority
> ---------------
>
> * `[TD0051]` Implement or remove the `CommonFileSystemExtractor` class.
>
> * `[TD0053]` Fix special case of collecting data from the `FileObject`.

### 2017-08-14

> High Priority
> -------------
>
> * `[TD0072]` __Think about adding a central "data pool" or manager.__  
>   Different components need to access data from other components, analyzer need
>   extracted data, plugins might need specific data to run. This is getting to
>   be pretty messy and difficult to handle. A possible solution might be to add
>   some kind of central handler or "repository" that store all data and state
>   for the current input path. This "data pool" or handler would be reset and
>   recreated for each of the processed input paths.
>
> * `[TD0074]` Implement means for components to access the shared session data.
>
> * `[TD0075]` __Consolidate data container classes.__  
>    Strive to simplify data structures, especially those that are passed across
>    program boundaries; between the "core" and extractors/analyzers/plugins,
>    etc. Reduce unnecessarily complex indirection and encapsulation, prefer
>    native data structures. Compared to plain dictionaries, the container
>    classes handle logging and error checking. But this could be just as well
>    be delegated to callers and accessors, and/or functions at boundaries.
>     * Remove/consolidate the `AnalysisResults` class.
>     * Remove/consolidate the `ExtractedData` class.

### 2017-08-03

> High Priority
> -------------
>
> * `[TD0067]` __Fix "destination exists" error when new name is same as old.__

### 2017-07-29

> High Priority
> -------------
>
> * `[TD0058]` Remove old unimplemented feature `--prepend-datetime`.

### 2017-07-28

> High Priority
> -------------
>
> * `[TD0006]` __New high-level architecture__
>     * Move to use the redesigned architecture
>     * All data extraction is handled by `extractor` classes
>     * `analyzer` classes do not perform any kind of data extraction.
>     * Plan for optimization by not extracting more data than necessary.
>       How could this be implemented?
>
> Medium Priority
> ---------------
>
> * `[TD0013]` Add conditional data extraction.
>     * Extractors should not run unless needed. Related to caching, above.
>
> * `[TD0050]` Figure out how to represent "null" for `datetime` types.

### 2017-07-27

> High Priority
> -------------
>
> * `[TD0005]` __Internal "API"__ -- communication between modules
>     * Replace the old way of calling the analyzer `get_{fieldname}` methods
>       with passing the `Analysis` class method `collect_results` as a callback.
>     * Fully implement the idea of dynamically constructing structures and
>       interfaces from a single reference data structure at runtime.

### 2017-07-25

> High Priority
> -------------
>
> * `[TD0003]` __Implement gathering data on non-core modules at run-time__
>     * Have extractors register themselves at run-time.
>     * Collect valid extractor query strings at run-time.
>     * Have analyzers register themselves at run-time.
>     * Collect valid analyzer query strings at run-time.
>     * Rework configuration validation to use dynamically updated tests.
>     * Replace hard coded strings with gathered data.
>
> Medium Priority
> ---------------
>
> * `[TD0022]` Look into merging possibly redundant methods `get` and `query` in
>   the `ExtractedData` class.
>
> * `[TD0021]` Look into merging possibly redundant methods `get` and `query` in
>   the `AnalysisResults` class.

### 2017-07-18

> High Priority
> -------------
>
> * `[TD0048]` Look into conflicting field parsers returned for metadata fields.
>   Especially the `DateTimeConfigFieldParser` and
>   `MetadataSourceConfigFieldParser` classes both want to handle some exiftool
>   fields.

### 2017-07-16

> High Priority
> -------------
>
> * `[TD0002]` __Add a custom type system__
>     * Add a abstract base class for all types (`BaseType`?)
>     * Wrap primitives in type classes inheriting from the base class
>       (`BaseType`?)
>     * Design type classes as to simplify upcoming query and comparison
>       operations performed while evaluating file rules; both "static"
>       conditions (basename equals this exact string/regexp) as well as
>       expressions (datetime data is within a given range)

### 2017-07-10

> High Priority
> -------------
>
> * `[TD0047]` __Improve determining `FieldParser` suitability__
>     * Add something similar to the "MIME type globbing" in
>       `fileobject.eval_magic_glob` for more flexible queries for
>       suitable `FieldParser` classes.
>
> * `[TD0001]` __Refactor the `Configuration` class__
>     * Look over all of `configuration.py`.
>     * Fix `eval_condition` in `core/evaluate/rulematcher.py`.
>     * Think about adding a custom type system in order to control configuration
>       parsing, evaluating file rule conditions and overall internal handling of
>       data.
>         * Types could fall back to safe defaults, avoid countless permutations
>           of "None-checking".
>         * Type classes could implement comparison/matching methods.

### 2017-07-09

> Medium Priority
> ---------------
>
> * `[TD0046]` Make sure that `FileRule` scores aren't shared between files.
>
> * `[TD0016]` __Enforce consistency in the configuration syntax.__
>   For example, why does the conditions for a file rule specify `extension`
>   under `filesystem`, while the results data structure has `extension` nested
>   under `filesystem.basename.extension`.
>
> High Priority
> -------------
>
> * `[TD0007]` __Pass all data to the `RuleMatcher` instance.__
>     * Currently, only the analysis data and data stored in the `FileObject`
>       is available when evaluating the rules. This hasn't been an obvious
>       problem due to the fact that the current implementation of rule
>       evaluation is so primitive and basic.

### 2017-06-30

> High Priority
> -------------
>
> * Simplify configuration file syntax.
>     * Modify the configuration file to use a "flatter" syntax.
>
> Low Priority
> ------------
>
> * `[TD0031]` Add compatibility checks when loading configuration.

### 2017-06-25

> Low Priority
> ------------
>
> * Implement handling directory input paths. Add `--recursive` option?

### 2017-06-24

> High Priority
> -------------
>
> * __New high-level architecture__ -- Move to use the redesigned architecture
>     * `analyzer` classes do not perform any kind of data extraction.
>         * Should data produced by `analyzer` classes be returned to a separate
>           container in the `Analysis` class?

### 2017-06-23

> High Priority
> -------------
>
> * __Text encoding issues__
>     * Add reusable translation layer that ensures proper handling of text
>       encoding of *all incoming textual data*;
>       standard input/output/error/.., path/file names, text file contents, etc.
>         * Decode all incoming data.
>         * Make sure the `encoding` parameter is always specified when reading
>           file contents with `open`.
>     * Add corresponding reusable translation layer for
>       *all outgoing textual data*.
>         * Encode all outgoing data.

### 2017-06-20

> High Priority
> -------------
>
> * Refactor the `NameBuilder` class and `namebuilder.py`
>     * Separate evaluating rules from constructing file names.
>     * Recreate something similar to the old `RuleMatcher` and have it handle
>       rule evaluation?

### 2017-06-19

> High Priority
> -------------
>
> * Update `MimeTypeConfigFieldParser` to handle MIME type globbing.

### 2017-06-17

> High Priority
> -------------
>
> * Handle case where `AnalysisResults` does not contain the data requested by
>   the name builder through the `query` method.

### 2017-06-16

> High Priority
> -------------
>
> ### New high-level architecture:
>
> * __The `Extraction` class controls all extractors__ --
>   The first step in the processing pipeline is calling the extractors that are
>   relevant to the current file.
>     * Data produced by `extractor` classes is returned to a new separate
>       container class `ExtractedData`.
> * __The `Analysis` class controls all analyzers__ --
>   Extracted data from `ExtractedData` is passed to the `Analysis` instance at
>   init.  Then the analyzers relevant to the file is called to process the data
>   returned by the extractors.
>
> ### Internal data storage
>
> * Think about distinguishing between *simple static data* and *derived data*.
>     * __"Static data":__ string `test.pdf`
>       (stored in results query field `filesystem.basename.full`)
>     * __"Derived data":__ `datetime`-object extracted from a UNIX timestamp
>       in `filesystem.basename.full`. Possibly stored as a dictionary with
>       the `datetile`-object in `data['value']`, along with `weight`, etc.
>     * Possibly additional types?
> * Should the "simple static" information be collected in a separate run?
> * Should the `Analysis` class `Results` instance only contain "simple static"
>   data? If so, use a separate container for "derived data".
> * Alternatively, store all types of results in the `Analysis` class `Results`
>   instance but modify the `Results` class to distinguish between the types?

### 2017-06-14

> High Priority
> -------------
>
> * __New high-level architecture__ -- Move to use the redesigned architecture
>     * Modify high-level program flow to something along the lines of:
>         1. Load configuration
>         2. Run all extractors that can handle the given file
>         3. Determine which configuration rule matches the given file
>         4. Enqueue analyzers based on the rule and extracted data
>         5. Run all enqueued analyzers
>         6. Assemble new file name from all available data
>
>         Having the extractor data available when evaluating rules (3) solves
>         the problem of evaluating certain conditions, like testing if the
>         given file contains a specific line of text, etc.
