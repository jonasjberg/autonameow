`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------


Ideas and Notes
===============
Various ideas on possible upcoming features and changes to `autonameow`.


Field Candidates
----------------
For cases where placeholder field data should be extracted from a document
text, the user should be able to control what content should be used.

For the placeholder field `title` for instance, the user might want to specify
a number of possible candidates. This would be done per file rule.
The candidates could be expressed as regular expressions or some other kind of
expression that would be evaluated against textual content extracted from
files.

* Control of data sources possible as of autonameow version `v0.4.4`:

    ```python
    'DATA_SOURCES': {
        'datetime': metadata.exiftool.PDF:CreateDate,
        'title': metadata.exiftool.XMP-dc:Title,
    }
    ```

* Possible redesigned configuration of data sources:

    ```python
    'DATA_SOURCES': {
        'datetime': { 
            # List of sources ordered by priority.
            'source': [metadata.exiftool.PDF:CreateDate,
                       metadata.exiftool.PDF:ModifyDate]
        }
        'title': {
            # Contents from source must match one of the regular expressions.
            'source': 'contents.textual.raw_text',
            'candidates': ['The Tale of Tail', 'The .* of .*', '^.* Tale .*$']
        }
    }
    ```

* Another possible variant of specifying sources:

    ```python
    'DATA_SOURCES': {
        'datetime': { 
            # List of sources ordered by priority.
            'source': [metadata.exiftool.PDF:CreateDate,
                       metadata.exiftool.PDF:ModifyDate]
        }
        'title': [
            # Raw text source is evaluated against two possible candidates.
            # If any expression evaluates true, "override" is used as the title.
            { 'source': 'contents.textual.raw_text',
              'candidates': [
                { 'expression': ['The Tale of Tail', 'The .* of .*', '^.* Tale .*$'],
                  'override': 'The Tale of Tail' },
                { 'expression': ['Catriarchy', 'Tuna Activism'],
                  'override': 'Gibson is Lord' }
              ]
            },
            # If the file basename (without extension) matches any of the two
            # expressions, "The Tale of Tail" is used as the title.
            { 'source': 'filesystem.basename.prefix',
              'candidates': [
                { 'expression': ['The-Tale-of-Tail', 'The-Tale-.*'],
                  'override': 'The Tale of Tail' },
              ]
            }
        ]
    }
    ```

    Here, the source specification of the `datetime` field is a simple list of
    two sources without any additional qualifier or expression.

    The `title` field can use any of two possible sources; the first source is
    the raw document text, that must match any of the given regular
    expressions.
    The second is the file basename without extension, that also must match one
    two expressions. In the case of a match, a hardcoded "`override`" is used
    as for the `title` field.

* Yet another way of configuring sources:

    ```python
    'DATA_SOURCES': {
        'title': {
            # Text from any of these two sources is to be considered.
            'source': [contents.textual.raw_text,
                       contents.textual.ocr_text],
            # Text from sources is searched for "match" and if found,
            # the text at "replace" is used for the title.
            'candidates': [
                {'match': 'The .* of .*',
                 'replace': 'The Tale of Tail'},
                {'match': '^Regex for Kittens ([1-9]+(st|nd|rd|th) [eE]dition)?$',
                 'replace': 'Regular Expressions for Kittens'}
            ]
        }
    }
    ```

    This way separates the sources from the candidates. The expressions in
    `match` could also be given as a list of expressions.



Notes on High-level Architecture
--------------------------------
About future additions of a frontends/GUIs.

### What is going on?

* __Program Operates on input:__ file(s)
* __Program Provides:__ New file names for the file(s)

Where/when are options presented and choices made?
Which could be presented in a GUI or in an *interactive mode*?

For any given file, how does the program come up with a new name?

What is required to come up with a new file name?

1. Select a __name template__
2. Populate the __placeholder fields__ in the template


#### Selecting a __name template__

* Chosen by the user
* Determined by the active configuration rule, chosen by the `RuleMatcher`

#### Populating the __placeholder fields__
How are the fields populated?

For each placeholder field, get some data that can be formatted to the fields
requirement (?).
The data could be either;

* Interactively chosen by the user
* Determined by the active configuration rule, chosen by the `RuleMatcher`

Which choices are presented to the user?
How are possible candidates collected?



Rule Matching Calculations
--------------------------

#### Alternative 1:
Calculating __score__ as `conditions_met / conditions_total` and
__weight__ as `conditions_met / max(len(rule.conditions) for rule in rules)`:

```
           CONDITIONS
           MET  TOTAL    Score   Weight     -->  Total scores?
  Rule A     1      2    0.5     0.2        -->  0.5*0.2 = 0.1
  Rule B     2      2    1       0.2        -->  1*0.2   = 0.2
  Rule C     5     10    0.5     0.5        -->  0.5*0.5 = 0.25
  Rule D    10     10    1       1          -->  1 * 1   = 1
```


#### Alternative 2:
Calculating __score__ as `conditions_met / conditions_total` and
__weight__ as `conditions_total / max(len(rule.conditions) for rule in rules)`:

```
           CONDITIONS
           MET  TOTAL    Score   Weight     -->  Total scores?
  Rule A     1      2    0.5     0.2        -->  0.5*0.2 = 0.1
  Rule B     2      2    1       0.2        -->  1*0.2   = 0.2
  Rule C     5     10    0.5     1          -->  0.5*1   = 0.5
  Rule D    10     10    1       1          -->  1 * 1   = 1
```


#### ~~Alternative 3:~~
~~Calculating __score__ as `conditions_met / conditions_total` and __weight__
as `conditions_total / sum(len(rule.conditions) for rule in rules)`:~~


```python
sum(len(rule.conditions) for rule in rules) # = 24
```

```
           CONDITIONS
           MET  TOTAL    Score   Weight     -->  Total scores?
  Rule A     1      2    0.5     0.083      -->  0.5*0.083 = 0.0415
  Rule B     2      2    1       0.083      -->    1*0.083 = 0.084
  Rule C     5     10    0.5     0.416      -->  0.5*0.416 = 0.208
  Rule D    10     10    1       0.416      -->    1*0.416 = 0.416
```



Data Transformation
-------------------
Thoughts on interactions between data-users (`NameBuilder`, analyzers) and
data-providers (extractors).

Data is collected by extractors and stored in the `SessionRepository`. This
data is "raw", I.E. consists of primitives and `datetime`-objects.

Some contextual metadata should be kept along with each stored data item for;

1. Conversion of "raw" data to fit a specific name template field.
    * The byte string `.jpg` to could populate the `{extension}` field by
      Unicode-conversion.
    * The MIME type (Unicode string) `image/jpeg` could also be used to
      populate the `{extension}` field, but some sort of __transformation__
      must be performed. *Likely using a lookup-table of MIME-types to file
      extensions.*
2. Ranking and prioritizing of results.
    * For example, EXIF metadata fields are often misused; the `author` field
      might not contain the author, the `producer` field might contain the
      publisher, etc.
    * Extractors could assign "probability" to extracted data.
      Example;
        ```python
        'PDF:Producer': ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.publisher, probability=0.25),
                fields.WeightedMapping(fields.author, probability=0.01)
            ]
        ```
    * ~~Alternatively, assigning semantic context and probabilities to the raw
      data could be handled by a separate process, after extraction.
      But the extractor that produced is probably in a better position to
      add additional contextual information or metadata to the data..~~


### Mapping "raw" data to name template placeholder fields
Expanding on the first item above.

* All available "raw" data is not equally suited to populate all of the
  placeholder fields.
* Some "raw" data sources is incompatible with certain placeholder fields.

A lot of "raw" data could probably be converted with varying results and
conversion losses.
For instance, `filesystem.contents.mime_type` could be "coerced" or converted
to some format appropriate for populating the template field `{title}`.

```
 'application/pdf'  -->  'PDF Document'
     Raw Data              Title Field
```

This specific example would probably require some kind of lookup-table or
heuristic to convert MIME-types to a equivalent human-readable "title"-like
form.


Some "raw" data will not relate to certain name template fields in any
meaningful way.  For example, `filesystem.contents.mime_type` can not be
transformed to a format suited for populating the template field `{datetime}`.

There is no way to transform a MIME type to date/time-information in a single
step.
The only way would be to "follow" the MIME-type data to some other related data
that might contain date/time-information.


### Example Practical Application
How would template fields map to actual "raw" data extracted from
`$AUTONAMEOW_SRCROOT_DIR/test_files/gmail.pdf`.


#### Example will be using the following name template fields:

* author
* date
* datetime
* description
* edition
* extension
* publisher
* tags
* title


#### Example will be using the following raw `SessionRepository` data:


```python
SessionRepository.data = {
    'metadata.exiftool.SourceFile': '/Users/jonas/PycharmProjects/autonameow.git/test_files/gmail.pdf',
    'metadata.exiftool.ExifTool:ExifToolVersion': 10.55,
    'metadata.exiftool.File:FileName': 'gmail.pdf',
    'metadata.exiftool.File:Directory': '/Users/jonas/PycharmProjects/autonameow.git/test_files',
    'metadata.exiftool.File:FileSize': 141636,
    'metadata.exiftool.File:FileModifyDate': datetime.datetime(2017, 6, 10, 16, 36, 18, tzinfo=datetime.timezone(datetime.timedelta(0, 7200)),),
    'metadata.exiftool.File:FileAccessDate': datetime.datetime(2017, 9, 3, 15, 41, 54, tzinfo=datetime.timezone(datetime.timedelta(0, 7200)),),
    'metadata.exiftool.File:FileInodeChangeDate': datetime.datetime(2017, 6, 10, 16, 36, 18, tzinfo=datetime.timezone(datetime.timedelta(0, 7200)),),
    'metadata.exiftool.File:FilePermissions': 644,
    'metadata.exiftool.File:FileType': 'PDF',
    'metadata.exiftool.File:FileTypeExtension': 'PDF',
    'metadata.exiftool.File:MIMEType': 'application/pdf',
    'metadata.exiftool.PDF:PDFVersion': 1.4,
    'metadata.exiftool.PDF:Linearized': False,
    'metadata.exiftool.PDF:PageCount': 2,
    'metadata.exiftool.PDF:Creator': 'Chromium',
    'metadata.exiftool.PDF:Producer': 'Skia/PDF',
    'metadata.exiftool.PDF:CreateDate': datetime.datetime(2016, 1, 11, 12, 41, 32, tzinfo=datetime.timezone.utc,),
    'metadata.exiftool.PDF:ModifyDate': datetime.datetime(2016, 1, 11, 12, 41, 32, tzinfo=datetime.timezone.utc,),
    'metadata.pypdf.Creator': 'Chromium',
    'metadata.pypdf.Producer': 'Skia/PDF',
    'metadata.pypdf.CreationDate': datetime.datetime(2016, 1, 11, 12, 41, 32, tzinfo=datetime.timezone.utc,),
    'metadata.pypdf.ModDate': datetime.datetime(2016, 1, 11, 12, 41, 32, tzinfo=datetime.timezone.utc,),
    'metadata.pypdf.creator': 'Chromium',
    'metadata.pypdf.producer': 'Skia/PDF',
    'metadata.pypdf.creator_raw': 'Chromium',
    'metadata.pypdf.producer_raw': 'Skia/PDF',
    'metadata.pypdf.Encrypted': False,
    'metadata.pypdf.NumberPages': 2,
    'metadata.pypdf.Paginated': True,
    'contents.textual.raw_text': '''1/11/2016 Gmail - .. TRUNCATED to 500/1981 characters)''',
    'filesystem.basename.full': 'gmail.pdf',
    'filesystem.basename.extension': 'pdf',
    'filesystem.basename.suffix': 'pdf',
    'filesystem.basename.prefix': 'gmail',
    'filesystem.pathname.full': '/Users/jonas/PycharmProjects/autonameow.git/test_files',
    'filesystem.pathname.parent': 'test_files',
    'filesystem.contents.mime_type': 'application/pdf',
    'filesystem.date_accessed': datetime.datetime(2017, 9, 3, 15, 41, 54,),
    'filesystem.date_created': datetime.datetime(2017, 6, 10, 16, 36, 18,),
    'filesystem.date_modified': datetime.datetime(2017, 6, 10, 16, 36, 18,),
    'analysis.filetags.description': 'gmail',
    'analysis.filetags.tags': [],
    'analysis.filetags.extension': 'pdf',
    'analysis.filetags.follows_filetags_convention': False,
}
```


#### Relationships between Raw data and Name Template Fields

| "MeowURI"                                       | Raw Data                                                             | Populateable (?) Fields                            |
|:------------------------------------------------|:---------------------------------------------------------------------|----------------------------------------------------|
| `'contents.textual.raw_text'`                   | `'''1/11/2016 Gmail - .. TRUNCATED to 500/1981 characters)'''`       | ?                                                  |
| `'filesystem.abspath.full'`                     | `'/Users/jonas/PycharmProjects/autonameow.git/test_files/gmail.pdf'` | ?                                                  |
| `'filesystem.basename.full'`                    | `'gmail.pdf'`                                                        | ?                                                  |
| `'filesystem.basename.extension'`               | `'pdf'`                                                              | `{extension}`                                      |
| `'filesystem.basename.suffix'`                  | `'pdf'`                                                              | `{extension}`                                      |
| `'filesystem.basename.prefix'`                  | `'gmail'`                                                            | ?                                                  |
| `'filesystem.pathname.full'`                    | `'/Users/jonas/PycharmProjects/autonameow.git/test_files'`           | ?                                                  |
| `'filesystem.pathname.parent'`                  | `'test_files'`                                                       | ?                                                  |
| `'filesystem.contents.mime_type'`               | `'application/pdf'`                                                  | `{extension}`                                      |
| `'filesystem.date_accessed'`                    | `datetime.datetime(2017, 9, 3, 15, 41, 54,)`                         | `{date}` `{datetime}`                              |
| `'filesystem.date_created'`                     | `datetime.datetime(2017, 6, 10, 16, 36, 18,)`                        | `{date}` `{datetime}`                              |
| `'filesystem.date_modified'`                    | `datetime.datetime(2017, 6, 10, 16, 36, 18,)`                        | `{date}` `{datetime}`                              |
| `'metadata.exiftool.ExifTool:ExifToolVersion'`  | `10.55`                                                              | ?                                                  |
| `'metadata.exiftool.File:FileSize'`             | `141636`                                                             | ?                                                  |
| `'metadata.exiftool.File:FileModifyDate'`       | `datetime.datetime(2017, 6, 10, 16, 36, 18)`                         | `{date}` `{datetime}`                              |
| `'metadata.exiftool.File:FileAccessDate'`       | `datetime.datetime(2017, 9, 3, 15, 41, 54)`                          | `{date}` `{datetime}`                              |
| `'metadata.exiftool.File:FileInodeChangeDate'`  | `datetime.datetime(2017, 6, 10, 16, 36, 18)`                         | `{date}` `{datetime}`                              |
| `'metadata.exiftool.File:FilePermissions'`      | `644`                                                                | ?                                                  |
| `'metadata.exiftool.File:FileType'`             | `'PDF'`                                                              | `{extension}`                                      |
| `'metadata.exiftool.File:FileTypeExtension'`    | `'PDF'`                                                              | `{extension}`                                      |
| `'metadata.exiftool.File:MIMEType'`             | `'application/pdf'`                                                  | `{extension}`                                      |
| `'metadata.exiftool.PDF:PDFVersion'`            | `1.4`                                                                | ?                                                  |
| `'metadata.exiftool.PDF:Linearized'`            | `False`                                                              | ?                                                  |
| `'metadata.exiftool.PDF:PageCount'`             | `2`                                                                  | ?                                                  |
| `'metadata.exiftool.PDF:Creator'`               | `'Chromium'`                                                         | `{author}` `{description}` `{publisher}` `{title}` |
| `'metadata.exiftool.PDF:Producer'`              | `'Skia/PDF'`                                                         | `{author}` `{description}` `{publisher}` `{title}` |
| `'metadata.exiftool.PDF:CreateDate'`            | `datetime.datetime(2016, 1, 11, 12, 41, 32)`                         | `{date}` `{datetime}`                              |
| `'metadata.exiftool.PDF:ModifyDate'`            | `datetime.datetime(2016, 1, 11, 12, 41, 32)`                         | `{date}` `{datetime}`                              |
| `'metadata.pypdf.Creator'`                      | `'Chromium'`                                                         | `{author}` `{description}` `{publisher}` `{title}` |
| `'metadata.pypdf.Producer'`                     | `'Skia/PDF'`                                                         | `{author}` `{description}` `{publisher}` `{title}` |
| `'metadata.pypdf.CreationDate'`                 | `datetime.datetime(2016, 1, 11, 12, 41, 32)`                         | `{date}` `{datetime}`                              |
| `'metadata.pypdf.ModDate'`                      | `datetime.datetime(2016, 1, 11, 12, 41, 32)`                         | `{date}` `{datetime}`                              |
| `'metadata.pypdf.Encrypted'`                    | `False`                                                              | ?                                                  |
| `'metadata.pypdf.NumberPages'`                  | `2`                                                                  | ?                                                  |
| `'metadata.pypdf.Paginated'`                    | `True`                                                               | ?                                                  |



Data Identifiers ("meowURIs")
-----------------------------
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


Thoughts on the "analyzers"
---------------------------
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

The "weighted field" that is currently part of the `ExtractedData` class is one possible method of providing context.
Extractors are probably best suited to give initial "value judgements" on the
data they extract. For any piece of extracted data; how likely is it correct?
Is it really what it says it is?

The analyzers should probably take this contextual information in consideration
when prioritizing candidates, etc.


Identify Fields in Strings
--------------------------
This is touched on in this TODO-list entry;

> * `[TD0019]` Rework the `FilenameAnalyzer`
>     * `[TD0020]` Identify data fields in file names.
>         ```
>         screencapture-github-jonasjberg-autonameow-1497964021919.png
>         ^___________^ ^__________________________^ ^___________^
>              tag            title/description        timestamp
>         ```
>         * Use some kind of iterative evaluation; split into parts at
>           separators, assign field types to the parts and find a "best fit".
>           Might have to try several times at different separators, re-evaluting
>           partials after assuming that some part is a given type, etc.
>         * __This is a non-trivial problem__, I would rather not re-implment
>           existing solutions poorly.
>         * Look into how `guessit` does it or possibility of modifying
>           `guessit` to identify custom fields.


### Ideas on Methods
Possible strategies for mapping fields to parts of strings.

#### Dates likely unique (date+time even more so)
Use the fact that probable dates, especially date+time; are likely to be
unique in a given context.

Given this example string, find fields `{datetime}` and `{whatever_}`:
```
2017-09-17 17092017
```

A fuzzy date-parser might identify two `YYYY-MM-DD` date-patterns in this
string, like so;

```
2017-09-17 17092017
YYYY-MM-DD DDMMYYYY
```
With only this information, we have two equally likely candidates for the
`{datetime}` field, and two equally unlikely candidates for the `{whatever_}`
field. Additional information is required ..

The context could be a common parent directory.
Lets say that there are multiple files in the same directory, we got two
example strings;
```
2017-09-17 17092017
2017-10-22 17092017
```

Now, if one were to apply the rule that date/time-strings are more likely
unique, the common substring `17092017` would be deemed less likely to be the
date/time-part.

#### Common "creator"/"artist"
Given a number of strings from a shared context, shared substrings are probably
often worth weighting.

__This should be done depending on context.__ 
*More stuff taken into account --> better accuracy.*

For example, trying to find fields `{artist}` and `{title}` given the strings;
```
Beatles, The - Paperback Writer.flac
Beatles, The - Getting Better.flac
```

Common substrings related to music files are probably more likely __artists__,
__albums__, etc.  And they are probably less likely to be song titles.

These assumptions will obviously prove incorrect a lot of times.

Applying the rule that `{artist}` is likely found in all/multiple files in a
given context;

```
Beatles The - Paperback Writer.flac
{ creator }   {    title     }


Beatles The - Getting Better.flac
{ creator }   {   title    }
```


### Programming by Wishful Thinking
Some yet non-existing system tries to identify specified fields in a given
string. Returns a list of substrings, sorted by score/ranking/weight.

```python
string = 'The Beatles - Paperback Writer.flac'

result = identify_fields(string, [field.Creator, field.Title])

assert result[fields.Creator] == ['The Beatles', 'Paperback Writer', 'flac',
                                  ' - ', '.']
assert result[fields.Title]   == ['Paperback Writer', 'The Beatles', 'flac',
                                  ' - ', '.']
```

Specifying __constraints__ or __rules__ --- require that both fields contain
at least one word character;
```python
string = 'The Beatles - Paperback Writer.flac'

add_constraint(field.Creator, matches=r'[\w]+')
add_constraint(field.Title, matches=r'[\w]+')
result = identify_fields(string, [field.Creator, field.Title])

assert result[fields.Creator] == ['The Beatles', 'Paperback Writer', 'flac']
assert result[fields.Title]   == ['Paperback Writer', 'The Beatles', 'flac']
```
