`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  
University mail: `js224eh[a]student.lnu.se`  

--------------------------------------------------------------------------------

`autonameow` Completed TODO-list entries
========================================

* 2017-07-25

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

* 2017-07-18

    > High Priority
    > -------------
    >
    > * `[TD0048]` Look into conflicting field parsers returned for metadata fields.
    >   Especially the `DateTimeConfigFieldParser` and
    >   `MetadataSourceConfigFieldParser` classes both want to handle some exiftool
    >   fields.

* 2017-07-16

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

* 2017-07-10

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

* 2017-07-09

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

* 2017-06-30

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

* 2017-06-25

    > Low Priority
    > ------------
    >
    > * Implement handling directory input paths. Add `--recursive` option?

* 2017-06-24

    > High Priority
    > -------------
    >
    > * __New high-level architecture__ -- Move to use the redesigned architecture
    >     * `analyzer` classes do not perform any kind of data extraction.
    >         * Should data produced by `analyzer` classes be returned to a separate
    >           container in the `Analysis` class?

* 2017-06-23

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

* 2017-06-20

    > High Priority
    > -------------
    >
    > * Refactor the `NameBuilder` class and `namebuilder.py`
    >     * Separate evaluating rules from constructing file names.
    >     * Recreate something similar to the old `RuleMatcher` and have it handle
    >       rule evaluation?

* 2017-06-19

    > High Priority
    > -------------
    >
    > * Update `MimeTypeConfigFieldParser` to handle MIME type globbing.

* 2017-06-17

    > High Priority
    > -------------
    >
    > * Handle case where `AnalysisResults` does not contain the data requested by
    >   the name builder through the `query` method.

* 2017-06-16

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

* 2016-06-14

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
