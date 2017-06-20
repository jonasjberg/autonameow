`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  
University mail: `js224eh[a]student.lnu.se`  

--------------------------------------------------------------------------------

`autonameow` Completed TODO-list entries
========================================


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
