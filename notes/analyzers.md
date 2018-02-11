`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Analyzers
=========
Notes on "analyzers" --- content-specific data providers.

#### Revisions
* 2017-10-15 --- `jonasjberg` Initial.
* 2018-01-18 --- `jonasjberg` Add section from `ideas.md`
* 2018-02-11 --- `jonasjberg` Move analyzer functionality to extractors?


Requirements
------------

* __Provide all possible data__  
    * Required when using the `--list-all` option and other similar cases
      where data providers are to be "queried" for which data could possibly
      be returned.

* __Provide specific data__
    * Currently implemented by querying the `Repository` for specific MeowURIs.
      The analyzers either does not run at all, or it runs and stores all data
      in the repository.


Structure of Returned Data
--------------------------
Compared to the extractors that return primitive data types, without context;
the analyzers are intended to work at the next level of abstraction.

The analyzers could return only specific fields, including "generic fields".
This could possibly eliminate the need to pass along information on the data
types; "coercer" class, whether it is "multivalued", etc.


Provider Mappings
-----------------
Should the analyzers be "mapped" as potential providers of certain kinds of
data, just like the extractors?
Maybe this should not be the case. I am starting to consider replacing the
concepts of "extractors" and "analyzers" with simply "providers" __if__ the
differences in intended use, functionality and implementation continues to be
this insignificant.


--------------------------------------------------------------------------------


Thoughts on the "analyzers"
---------------------------
> Jonas Sjöberg, 2017-09-15.

The "analyzer" classes was added very early in the development where it looked
nothing like what its current state. The overall design ideas has changed
dramatically, and so the analyzer classes, as they are current implemented,
does not belong in the project.

They should be rewritten and redesigned as to handle __specific content__, as
opposed to the initial idea of having the handle *specific files*.

The recent reworking of the `PdfAnalyzer` to a `DocumentAnalyzer` is the first
example of updating the old analyzers.

### Differences between extractors and analyzers:

* __Extractors:__
    * __Extracts data__ (content, metadata) from files on disk.
    * __Handles specific MIME-types__. I.E. different extractors are used for
      different __file formats__.
    * __Converts data to an "internal format"__ or common representation that
      is used by the rest of the program components, such as analyzers,
      plugins, name builder, etc.

* __Analyzers:__
    * __Analyzes data__ (metadata) from data produced by extractors.
    * __Handles specfic types of contents__. The `EbookAnalyzer` deals with
      e-books, etc.
    * __Provides a "bigger picture" understanding of extracted data__.
      Finds most likely candidates using routines tailored for specific types
      of content. Which date/time-information is most likely "correct"?

### Contextual information
The analyzers should be provided with *contextual information*.

The "weighted field" that is currently part of the `ExtractedData` class is one
possible method of providing context.
Extractors are probably best suited to give initial "value judgements" on the
data they extract. For any piece of extracted data; how likely is it correct?
Is it really what it says it is?

The analyzers should probably take this contextual information in consideration
when prioritizing candidates, etc.


--------------------------------------------------------------------------------


Analyzers vs. Extractors
------------------------
> Jonas Sjöberg, 2018-02-11.

As mentioned somewhere, elsewhere, the differences between the analyzers and
Extractors might not be enough to motivate keeping this separation of
abstraction.

The filename analyzer might just as well be an extractor that finds possible
field data in filenames. But then again, maybe some "contextual information" is
required to avoid producing poor results, false positives.  If the filename
analyzer was to be executed like the extractors, I.E. very simple interface
like;

```python
a = FilenameAnalyzer()
results = a.analyze(file)
```

What means would really be available in order to make sense of the available
data and produce quality results? The only thing that comes to mind right now
is plain pattern matching. This could be made somewhat sophisticated with
dynamic white/black-lists, etc. But in this case, some other kind of entity
will likely need to go through the resulting data again in order to weed out
bad results and find the data that is most relevant for that current execution
context, requirements, etc.

Irregardless, there is a major problem of code duplication to be solved.  A lot
of code is practically equivalent in the systems that interface to and
orchestrate execution of extractors, analyzers and plugins. Similarly when
passing results around, etc.
