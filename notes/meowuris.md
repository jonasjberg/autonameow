`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------

Data Identifiers ("MeowURIs")
=============================
Notes on the internal data identifier system and "MeowURI" naming convention.

#### Revisions
* 2017-09-09 --- `jonasjberg` Initial.
* 2017-09-23 --- `jonasjberg` Added notes from `ideas.md`
* 2017-09-27 --- `jonasjberg` Added "Breaking up MeowURIs into Parts"
* 2017-09-28 --- `jonasjberg` Added "Alternative approach 3"
* 2018-02-21 --- `jonasjberg` Rework hierarchical structure and naming.
* 2018-04-18 --- `jonasjberg` Metadata processing layer positioning


--------------------------------------------------------------------------------


Field Normalization, Filtering and other Processing
---------------------------------------------------
> Jonas Sjöberg, 2018-04-18.

*Where should a metadata "pre-processing" system be inserted?*

Related to the above notes on how URIs would be increasingly specific when longer.

Currently, a MeowURI like `extractor.metadata.exiftool.PDF:Title` might return
`MILLER & FREUND’S PROBABILITY AND STATISTICS FOR ENGINEERS; NINTH EDITION Global Edition`.

I.E. a query with an URI like `extractor.metadata.exiftool.PDF:Title` that should
return a value `{title}` actually returned `{publisher} {title} {edition} {edition}`.

```
MILLER & FREUND’S PROBABILITY AND STATISTICS FOR ENGINEERS; NINTH EDITION Global Edition
{_ publisher _}   {_______________ title ________________}  {_ edition _} {_ edition? _}
```

This is related to `[TD0192]` on extracting editions from titles and general
Handling of field values with parts that really belong in another separate
field.

Maybe this should be as it is; a means of accessing a specific field value from
a specific source with no/little changes made by `autonameow`.

Then a "less specific" URI like `extractor.metadata.title` would take all
available title-like field values, process them, run de-duplication, detect
fields within fields, etc.

Then `extractor.metadata.title` might just return `PROBABILITY AND STATISTICS
FOR ENGINEERS` if that is the only value available (like `XMP:Title`, etc.)
__or a list__ of all title-like values produced by exiftool.

* Do minimal provider-specific processing of metadata returned by "full" URIs.
* Do processing, "field-in-field" detection, etc. of metadata returned by
  "less specific" or "implicit" URIs.


--------------------------------------------------------------------------------


Flexibility in Actual Usage
---------------------------
> Jonas Sjöberg, 2018-02-20.

The original idea for efficient command-line usage is speed through logical
order and autocompletion.  Actual usage is currently not very good.
MeowURI naming and hierarchical structure must be done properly.


### How about this?

Like climbing down a hierarchy, from most to least specific.


Example requesting the `description` field:

1. Full "direct" lookup from a single specific provider `filetags`:

        extractor.filesystem.filetags.DESCRIPTION

2. From any of the `filesystem` providers:

        extractor.filesystem.DESCRIPTION

2. From any of the `extractor` group of providers:

        extractor.DESCRIPTION

3. from __any/all__ of the available providers:

        DESCRIPTION

    This is currently called "generic" MeowURIs, written as:
    ```
    generic.metadata.DESCRIPTION
    ```

If only one provider has produced data with a `description` field, all of the
above would return the same result.


~~And again, restated:~~

When the "leaf" position shifts from the first to last position of the full
MeowURI, the data query becomes increasingly explicit and direct.

```
 specific:  a.b.c.X
            a.b.X
            a.X
"generic":  X
```

~~Might think of it like a tree structure of `X` nodes that all refer to the same
piece of information.~~

* `X` --- any `X`
* `a.X` --- `X` within subtrees of `a` (from any children of `a`)
* `a.b.X` --- `X` within subtrees of `b` (child of `a`)
* `a.b.c.X` --- `X` within subtrees of `c` (child of `b` which is child of `a`)


--------------------------------------------------------------------------------


Might visualize it like this:
 *Think about if this general case is actually what is used?*

```
a ________________________________________________________
  x1  x2        x3          x4                        x5


b __________________    c ____________________    d ______
  x1  x2        x3          x5                         x6


e ______    f ______    g ______    h ________    i ______
  x1  x2        x3          x4                        x5
```

* Top is the "root"
* Middle `b` to `d` are provider groups (extractors, analyzers, plugins)
* Bottom `e` to `i` are actual providers (filesystem extractor, ebook analyzer, etc.)


So queries with MeowURIs;

* `a.b.e.x` would return values `x1` and `x2`
* `a.b.x` would return values `x1`, `x2` and `x3`
* `a.x` would return all values `x1` through `x5`


### Or how about this?
These are all title-related MeowURIs:

```
(generic.metadata.title)
analyzer.document.title
extractor.filesystem.guessit.title
extractor.metadata.exiftool.PDF:Title
extractor.metadata.exiftool.RTF:Title
extractor.metadata.exiftool.XMP:EntryTitle
extractor.metadata.exiftool.XMP:Title
extractor.metadata.pandoc.title
```

I might want to get a specific exiftool field:
```
extractor.metadata.exiftool.PDF:Title
```

Any exiftool title:
```
extractor.metadata.exiftool.title
```
Any exiftool title, alternative (?):
```
extractor.exiftool.title
```

Any title:
```
title
```
(this is currently `generic.metadata.title`)


Any __metadata__ title:
```
metadata.title
```
__This would not be possible with the new plan__ (?)



As a table:


(generic.metadata.title)
analyzer.document.title
extractor.filesystem.guessit.title

extractor.metadata.exiftool.PDF:Title
extractor.metadata.exiftool.RTF:Title
extractor.metadata.exiftool.XMP:EntryTitle
extractor.metadata.exiftool.XMP:Title
extractor.metadata.pandoc.title



Problems with the "MeowURI" abstraction
---------------------------------------

### Replacing `basename_full` with `basename.full`
Using leaves consisting of a single part makes sense in that mapping
between "external" and "internal" field names is straight-forward.

Providers return "raw" data as dicts:
```python
raw_metadata = {
    'PDF:CreateDate': '2018-02-21'
}
```

Which is then collected by the various runners and stored with the full
MeowURI:
```python
provider_metadata = {
    'extractor.metadata.exiftool.PDF:CreateDate': {
        'value': '2018-02-21',
        'metainfo': '...'
    }
}
```

The external keys (`PDF:CreateDate`) can easily be swapped with whatever.

For leaves that must be referred to as a two-part string, things become complicated.


Providers return "raw" data as dicts:
```python
raw_metadata = {
    'basename': {
        'full': 'foo'
    }
}
```

Which is then collected by the various runners and stored with the full
MeowURI:
```python
provider_metadata = {
    'extractor.filesystem.xplat.basename.full': {
        'value': 'foo',
        'metainfo': '...'
    }
}
```


At the same time, how many possible providers would provide the full basename
of a file?  It would not add any value whatsoever. So maybe the user-facing
MeowURIs __should__ split the leaf in two parts?


__This is probably the way to go, discoverability through
auto-complete/suggestions in the CLI interface.__

Might simply translate `_` to `.` somewhere at the UI layer boundaries.

#### Related TODOs:

> * `[TD0162]` Handle mapping/translation between "generic"/specific MeowURIs.
>
> * `[TD0125]` __Add aliases (generics) for MeowURI leafs__  
>   Should probably provide a consistent internal alternative field name when
>   specifying extractor-specific MeowURIs, not only with "generic".
>
>   Example of equivalent MeowURIs with the "alias" or "generic":
>
>     ```
>     extractor.metadata.exiftool.PDF:CreateDate
>     extractor.metadata.exiftool.date_created
>     ```
>
>   Another example:
>
>     ```
>     extractor.metadata.exiftool.EXIF:DateTimeOriginal
>     extractor.metadata.exiftool.date_created
>     ```
>   The examples illustrate that multiple provider-specific fields would have to
>   share a single "alias" or "generic", because there will always be fewer of
>   them. If these were not based on the subclasses of `GenericField`, they could
>   simply be made to map directly with the provider fields, maybe only with a
>   slight transformation like converting to lower-case.
>
>   Example of alternative using simple transformations:
>
>     ```
>     extractor.metadata.exiftool.EXIF:DateTimeOriginal
>     extractor.metadata.exiftool.exif_datetimeoriginal
>     ```
>
> * `[TD0089]` Validate only "generic" data fields when reading config.
>
> * `[TD0146]` Rework "generic fields", possibly collecting fields in "records".


### Mapping configuration field parsers and other "globbing"
Probably does not matter as it should be reworked anyway?


--------------------------------------------------------------------------------


Data Storage
============
Data is stored in the `Repository` data store, identified by a
`FileObject` and a "MeowURI".


Simplified example of data storage:
```python
file_object = FileObject('/tmp/foo/bar.txt')
data = file_object.abspath
Repository.store(file_object, 'filesystem.pathname_full', data)
```

The data can then be retrieved by querying the repository:
```python
data = Repository.query(file_object, 'filesystem.pathname_full')
```


The "MeowURI" identifiers are currently, as of 2017-09-09 (commit
b402ae3211fec7f4b5bd66eddf0d72d4cfc94c04) arranged as follows:



__Extractors__ store data without any special prefix;

```
filesystem.basename_full
filesystem.mime_type
metadata.exiftool.EXIF:DateTimeOriginal
metadata.exiftool.QuickTime:CreationDate
metadata.exiftool.XMP-dc:Creator
```


__Analyzers__ store data with the prefix `analyzer`;

```
analyzer.document.title
analyzer.document.author
analyzer.ebook.author
analyzer.ebook.title
analyzer.ebook.publisher
```


The "MeowURI" naming convention has been changed a lot and should be cleaned up.
Maybe it would be helpful to add a prefix to the extractor URIs.


Usability and Generic Fields
============================
Currently, the available identifiers strings, a.k.a. "MeowURIs" use
extractor-specific "leaf-nodes", I.E. last period-separated part.

For instance;

```
metadata.exiftool.PDF:CreateDate
                  |____________|___.--< Last part
                                        ("leaf node")
```

The usability of this arrangement is very poor ..
Users might not care about which specific extractor produced the field data,
but rather that *some* information about the date of creation is available.

This would require translating extractor-specific fields with roughly
equivalent semantic meanings.
One possibility is to translate extractor-specific identifiers to a common
higher-level interface to fields.

For example;
```
Extractor-specific "MeowURIs", references specific fields:
    metadata.pypdf.CreationDate
    metadata.exiftool.PDF:CreateDate

Proposed interface, alternate access to "any" equivalent field:
    metadata.DateCreated
```

Note that the proposed field query still only references metadata sources.

If the session repository contains the following data for a given file object:

| "MeowURI"                            | Raw Data                            |
|:-------------------------------------|:------------------------------------|
| `'metadata.pypdf.CreationDate'`      | `datetime(1972, 2, 23, 11, 22, 33)` |
| `'metadata.exiftool.PDF:CreateDate'` | `datetime(2017, 9,  5, 14, 07, 31)` |


Querying the repository for;

* `'metadata.pypdf.CreationDate'` returns `datetime(1972, 2, 23, 11, 22, 33)`
* `'metadata.exiftool.PDF:CreateDate'` returns `datetime(2017, 9,  5, 14, 07, 31)`

And additionally, the proposed change would allow querying for;

* `'metadata.DateCreated'` returns `[datetime(1972, 2, 23, 11, 22, 33),
  datetime(2017, 9,  5, 14, 07, 31)]`

Additionally, the returned list could contain contextual information; weights,
scores, priorities, etc.
The less specific query would require the program to take responsibility for
selecting the appropriate field.

## Update 2017-09-13
I'm currently in the process of adding some kind of "generic" field that,
if defined, allows referencing data using two different "MeowURIs";
*source-specific* and *generic*

### Examples from the current implementation;
These two data entries are stored in the repository with
source-specific MeowURIs:

* `metadata.exiftool.File:MIMEType: application/pdf`
* `filesystem.mime_type: application/pdf`

They are also stored under a "generic URI":

* `contents.generic: [application/pdf, application/pdf]`

### Current conundrum
I can't decide on how to lay out the "alternate" URIs.
How should they be nested for usability and consistency?

Below examples show different schemes specific and generic "MeowURIs"
storing data "elements"; `D1`, `D2`, `D3`, `D4`.

#### Current approach:

* Source-specific URIs:
    * `filesystem.mime_type: D1`
    * `metadata.exiftool.File:MIMEType: D2`
    * `metadata.pypdf.CreationDate: D3`
    * `metadata.exiftool.PDF:CreateDate: D4`
* Generic URIs:
    * `contents.generic.mimetype: [D1, D2]`
    * `metadata.generic.datecreated: [D3, D4]`

#### Alternative approach 1:

* Source-specific URIs:
    * `filesystem.mime_type: D1`
    * `metadata.exiftool.File:MIMEType: D2`
    * `metadata.pypdf.CreationDate: D3`
    * `metadata.exiftool.PDF:CreateDate: D4`
* Generic URIs:
    * `generic.contents.mimetype: [D1, D2]`
    * `generic.metadata.datecreated: [D3, D4]`

#### Alternative approach 2:

* Source-specific URIs:
    * `filesystem.mime_type: D1`
    * `metadata.exiftool.File:MIMEType: D2`
    * `metadata.pypdf.CreationDate: D3`
    * `metadata.exiftool.PDF:CreateDate: D4`
* Generic URIs:
    * `contents.mimetype: [D1, D2]`
    * `metadata.datecreated: [D3, D4]`


#### Pros/Cons
I'm currently in favor of "Alternative approach 2" because it seems simpler
to just leave out the source part .. (?)

~~(It should also maybe possibly be easier to integrate into the existing
codebase as it currently stands..)~~

Going with "Alternative approach 2" would allow referring to data like this:

* Specific retrieval: `metadata.pypdf.creator`
    * Fetches specific data from a specific source.
    * Returns either nothing at all or __one__ data "element".
* Generic retrieval: `metadata.creator`
    * Fetches "equivalent" data from any sources.
    * Returns nothing, __or any number__ of data "elements".

Also; it might make sense to keep a URI-node (like `.generic.`) in the MeowURIs
to clearly separate the types, which might be helpful for the implementation.
In this case, it probably wouldn't be very difficult to translate from a
"internal" URI like `generic.contents.mimetype` or `contents.generic.mimetype`
to a simplified form, used in all user interfaces; `mime_type` ..


Going with "Alternative approach 2"
-----------------------------------
Going the "Alternative approach 2" mentioned above means having to solve;

* __Validating MeowURIs__, E.G. when parsing the configuration.
* Handling MeowURIs when __storing data in the repository__.
* Handling MeowURIs when __retrieving data from the repository__.

### Breaking up MeowURIs into Parts

#### Source-specific URIs:
```
  MeowURI:      extractor . metadata . exiftool . File:MIMEType
              |-----------|----------|----------|---------------|
Part Type:    '   ROOT    '  CHILD   '  CHILD   '     LEAF      '
   Origin:     (constant)  (package)   (module)    (dict key)
```

```
  MeowURI:      extractor .  text  .  plain  . full
              |-----------|--------|---------|------|
Part Type:    '   ROOT    ' CHILD  '  CHILD  ' LEAF '
   Origin:     (constant)  (package)(module) (dict key)
```

Example of inconsistencies when the last two parts of a MeowURI from from
a dictionary:
```
  MeowURI:      extractor . filesystem . xplat . contents . mime_type
              |-----------|------------|-------|----------|-----------|
Part Type:    '   ROOT    '   CHILD    ' CHILD '  CHILD?  '   LEAF    '
                                                   LEAF?
   Origin:     (constant)    (package)   (??)    ^--- (dict keys) ---^
```

#### Generic URIs:
```
  MeowURI:      generic . contents . mimetype
              |---------|----------|----------|
Part Type:    '   Root  '  CHILD   '   LEAF   '
   Origin:     (constant)   (??)       (??)
```

Introducing "Alternative approach 3"
------------------------------------
I have thought about this and performed some more experiments.

### Extractors
Lets say there are two main types of MeowURIs for extractors;
__source-specific__ and __generic__.

#### Extractor --- Source-Specific
The current implementation uses the Python package hierarchy to construct the
center MeowURI nodes (children) for source-specific MeowURIs.

Take for instance `extractor.metadata.exiftool.File:MIMEType`, consisting of;

* `extractor` -- all classes inheriting from `BaseExtractor` use this prefix
* `metadata` -- Python package name
* `exiftool` -- Python module name
* `File:MIMEType` -- Derived from dictionary key returned by the extractor

It might be better to drop the unneeded parts.

__Suggested new form:__  `extractor.exiftool.file:MIMEType`

#### Extractor --- Generic
The current generic form is constructed from definitions in subclasses of
`GenericField`. They all share the prefix `generic` defined by a constant.

Take for instance `generic.metadata.description`, consisting of;

* `generic` -- all classes inheriting from `GenericField` use this prefix
* `metadata` -- class attribute in the `GenericDescription` class
* `description` -- class attribute in the `GenericDescription` class

The source-specific MeowURIs start with either `extractor`, `plugin` or `analyzer`.
So there really is no need for the `generic`-part to distinguish the types.

__Suggested new form:__  `metadata.description`

### Analyzers
Analyzers only really expose a internal naming convention.

There might not be any need to use "generic" analyzer-URIs (?)
