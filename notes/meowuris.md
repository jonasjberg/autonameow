`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Data Identifiers ("MeowURIs")
=============================
Notes on the internal data identifier system and "MeowURI" naming convention.

#### Revisions
* 2017-09-09 --- `jonasjberg` Initial.
* 2017-09-23 --- `jonasjberg` Added notes from `ideas.md`
* 2017-09-27 --- `jonasjberg` Added "Breaking up MeowURIs into Parts"
* 2017-09-28 --- `jonasjberg` Added "Alternative approach 3"


Data Storage
============
Data is stored in the `Repository` data store, identified by a
`FileObject` and a "MeowURI".


Simplified example of data storage:
```python
file_object = FileObject('/tmp/foo/bar.txt')
data = file_object.abspath
Repository.store(file_object, 'filesystem.pathname.full', data)
```

The data can then be retrieved by querying the repository:
```python
data = Repository.query(file_object, 'filesystem.pathname.full')
```


The "MeowURI" identifiers are currently, as of 2017-09-09 (commit
b402ae3211fec7f4b5bd66eddf0d72d4cfc94c04) arranged as follows:



__Extractors__ store data without any special prefix;

```
filesystem.basename_full
filesystem.contents.mime_type
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


__Plugins__ store data with the prefix `plugin`;

```
plugin.microsoft_vision.caption
plugin.microsoft_vision.tags
plugin.guessit.date
plugin.guessit.title
```


The "MeowURI" naming convention has been changed a lot and should be cleaned up.
Maybe it would be helpful to add a prefix to the extractor URIs.


Usability and Generic Fields
============================
Currently, the available identifiers strings, a.k.a. "meowURIs" use
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
Extractor-specific "meowURIs", references specific fields:
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
* `filesystem.contents.mime_type: application/pdf`

They are also stored under a "generic URI":

* `contents.generic: [application/pdf, application/pdf]`

### Current conundrum
I can't decide on how to lay out the "alternate" URIs.
How should they be nested for usability and consistency?

Below examples show different schemes specific and generic "MeowURIs"
storing data "elements"; `D1`, `D2`, `D3`, `D4`.

#### Current approach:

* Source-specific URIs:
    * `filesystem.contents.mime_type: D1`
    * `metadata.exiftool.File:MIMEType: D2`
    * `metadata.pypdf.CreationDate: D3`
    * `metadata.exiftool.PDF:CreateDate: D4`
* Generic URIs:
    * `contents.generic.mimetype: [D1, D2]`
    * `metadata.generic.datecreated: [D3, D4]`

#### Alternative approach 1:

* Source-specific URIs:
    * `filesystem.contents.mime_type: D1`
    * `metadata.exiftool.File:MIMEType: D2`
    * `metadata.pypdf.CreationDate: D3`
    * `metadata.exiftool.PDF:CreateDate: D4`
* Generic URIs:
    * `generic.contents.mimetype: [D1, D2]`
    * `generic.metadata.datecreated: [D3, D4]`

#### Alternative approach 2:

* Source-specific URIs:
    * `filesystem.contents.mime_type: D1`
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
to a simplified form, used in all user interfaces; `contents.mime_type` ..


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
