`autonameow`
============
*Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------

Ideas and Notes
===============
Various ideas on possible upcoming features and changes to `autonameow`.

#### Revisions
* 2017-07-25 --- `jonasjberg` Initial
* 2017-09-25 --- `jonasjberg` Add notes on the "Resolver"
* 2017-09-28 --- `jonasjberg` Add notes on auto-completing MeowURIs.
* 2017-10-14 --- `jonasjberg` Add thoughts on a reasoning/probability system.
* 2017-10-28 --- `jonasjberg` Using a proper Metadata Repository.
* 2018-01-18 --- `jonasjberg` Move section to other file.
* 2018-01-30 --- `jonasjberg` Add "Decision Rules for Attribute-Based Choices".
* 2018-03-03 --- `jonasjberg` Notes on "reasoning" and probabilities.


--------------------------------------------------------------------------------


Notes on "reasoning" and Probabilities
--------------------------------------
> Jonas Sjöberg, 2018-03-03.


Subset of current problems and possible solutions:

1. Deduplication of (ISBN) metadata records
    * Replace hardcoded threshold field comparison values
    * Adjust values based on domain knowledge?
    * Supervised learning by involving the user? How?

2. Named entity recognition
    * Find likely titles, publishers, etc. in unstructured text.
    * Adjust values based on (hardcoded) domain knowledge?  
      *Titles in documents published by X is likely within lines 1-3 ..*
    * Automated learning? Where is the "feedback-loop"?  
      *Use selection from candidates by the user as positive examples?*

3. Candidate weighting/ranking
    * Learn from previous renames?  
      *If 99% of all previous metadata sets containing `publisher: foo`
      contained a correct `author` field, assume it is likely correct?*
    * How much example data can be stored and evaluated in a reasonable time?

4. Classification of file name substrings


### Deduplication of metadata records
Given two records that probably should be considered equivalent:

```python
a = {
    'author': 'Sjöberg G.',
    'title': 'Meow Meow',
    'year': 2018,
}

b = {
    'author': 'Gibson Sjöberg',
    'title': 'Meow! Meow!',
    'year': 2018,
}
```

Each field is compared using a suitable comparison function that returns a
float between 0 and 1.
Simple comparison of the records would calculate a weighted average
similarities between the separate fields.

Dummy field comparison results:

| Field   | Record A value      | Record B value  | Similarity  | Difference |
| ------- | ------------------- | --------------- |:----------- |:---------- |
| author  | Gibson Cat Sjöberg  | Gibson Sjöberg  | 0.78        | 0.22       |
| title   | Meow Meow           | Meow! Meow!     | 0.82        | 0.18       |
| year    | 2018                | 2018            | 1.00        | 0.00       |


Then one might calculate the record similarity as:

$R_{similarity} = (0.78 + 0.82 + 1.00) / 3$

$R_{similarity} = w * 0.78 + w * 0.82 + w * 1.00$

.. with $w = 1/3$. I.E. equally weighted average.


But field weights will likely need to adjusted separately to yield better
results.

$R_{similarity} = w_{a} * 0.78 + w_{b} * 0.82 + w_{c} * 1.00$

Also, given a final record similarity score between 0 and 1.
How would one pick a threshold value for whether the records should be
considered equivalent?


__Open questions:__

* What information should be used to modify the weights $w_{a}$, $w_{b}$, $w_{c}$?
* What information should be used to modify the record similarity threshold?
* Apply previously learned weights/thresholds based on certain fields having specific values?
* Could application of weights/thresholds based on values itself be weighted?
* How meta can this become while remaining practical and relatively fast?
* How flexible should "routing" of "weight/threshold controllers" be?
* What is practical and actually effective?


### Named entity recognition
Using some kind of universal text parser that converts multiple document
formats to a single known format, with markup/semantics/structure intact, would
probably be a lot easier.
But this only works for source text that is structured and valid; as in
´START_TITLE foo END_TITLE`, where *foo* might not actually be the title. The
author might have used the markup to change the appearance, ignoring the
structure *(E.G. typical mis-use of MS Word, etc..)*

__Assuming that we'll work with unstructured text .._

Given some raw, unstructred text:
```
A
MEOW
TITLE

by Gibson
Catson

foo
```

We'd like to see this output when analyzing the text:

```python
results = {
    'title': 'A MEOW TITLE',
    'author': 'Gibson Catson'
}
```

Could probably find a "very abstract" generalization of commonalitites between
several heuristics.  Where a "heuristic" might be to assume a "entity" is
always constrained to a single line.  Then, absolute line number as well as
line number relative to other candidate entities could be the main features.


Or maybe something along the lines of blocks, like so;

```
        .->   A                   Block A -->   A MEOW TITLE
Block A |     MEOW
        '->   TITLE
                                  block C -->   foo
Block B -->   by Gibson
        '->   Catson              Block B -->   by Gibson Catson

Block C -->   foo
```

Where the condition for termination a block is variable.
Each block could be turned into simple feature vectors by word count, character
count, capitalization, position, number of lnie breaks, etc.



### Classification of file name substrings
Like above, with a lot more constraints --- always a single line of text, etc.


--------------------------------------------------------------------------------


Thoughts on Implementing a ("reasoning") Probability System
-----------------------------------------------------------
> Jonas Sjöberg, 2017-10-14.


*It has been obvious for quite some time that `autonameow` needs to integrate
ideas and techniques from machine learning and probabilistic programming to
solve some of the main problems.*

*These are fields that I have no prior experience with, whatsoever..  But, here
are some high-level ideas of problems that have already been solved, better..*

Lets say the program component `FilenameTokenizer` was given the file name
`A%20Quick%20Introduction%20to%20IFF.txt` and has managed to detect that the
filename is URL-encoded, etc and finally came up with this result:
`['A', 'Quick', 'Introduction', 'to', 'IFF.txt']`

Which is pretty good. But the separator-detection would like additional
information in order to figure out how to split the last element `IFF.txt`.

The main point is this:
__Parts of the system need to "ask" other parts to verify propositions__

In this case, the `FilenameTokenizer` would like to know if the `.txt` part of
`IFF.txt` is a file extension or not.

It would be nice if there was a system so that the `FilenameTokenizer` could
pass this question to some central point, that could figure out which parts of
the system that are able to answer the question.

Given the question;
__Given the string `IFF.txt`, is the substring `.txt` a file extension?__;
these sources could possibly provide relevant evidence:

- Check if the MIME-type of the related file (if any) is `text/plain`:
    ```python
    >>> _ext = 'IFF.txt'.split('.')[-1]
    >>> _ext
    'txt'
    >>> from core import coercers
    >>> coercers.AW_MIMETYPE(_ext)
    'text/plain'
    ```

* Check the extension provided by the related `FileObject` (if any):
    ```python
    >>> f = FileObject(b'/Users/jonas/today/A%20Quick%20Introduction%20to%20IFF.txt')
    >>> f
    <FileObject("/Users/jonas/today/A%20Quick%20Introduction%20to%20IFF.txt")>
    >>> f.basename_suffix
    b'txt'
    ```

Then add weights to the results of the evidence and calculate a __total
probability score__.

In this case, the MIME-type test would probably be weighted by `10`, so that a
failed evaluation decreases the total score a lot.

The `FileObject` evidence, along with other potential sources of information
related to file extension, would probably be weighted a bit lower.

Everything would be combined and returned as an answer to the question
originally posed by the `FilenameTokenizer` component.


--------------------------------------------------------------------------------


Using a proper Metadata Repository
----------------------------------
> Jonas Sjöberg, 2017-10-28.


The current means of central storage uses the `Repository` class to store all
data in a simple two level key-value store.
The first primary key (level 1) is the `FileObject` that produced the data.
These contain values keyed by `MeowURI` (level 2).


### "Proper" Metadata Repositories

> Metadata repository not only stores metadata like Metadata registry but also
> adds relationships with related metadata types.
>
> <https://en.wikipedia.org/wiki/Metadata_repository>

Blog post on nomenclature: [Metadata Repositories vs. Metadata
Registries](http://datadictionary.blogspot.se/2008/03/metadata-repositories-vs-metadata.html)

### Retrieval
The current system is far from being able to arrange and retrieve data
"dynamically", using relational queries. This would sometimes be very useful..

### Primary Keys
One specific general case is metadata that share a single unique identifier,
like ISBN-numbers. This is currently not easy to implement.


--------------------------------------------------------------------------------


Decision Rules for Attribute-Based Choices
------------------------------------------
Possible methods of weighting when prioritizing candidate data.


* __Conjunctive Rule__  
    Establishes minimum required performance for each evaluative criterion.

    Selects the first (or all) item(s) that meet or exceed these minimum
    standards.

* __Disjunctive Rule__  
    Establishes a minimum required performance for each important attribute.
    All items that meet or exceed the performance level for __any__ key
    attribute are acceptable.

* __Elimination-by-Aspects Rule__  
    First, evaluative criteria ranked in terms of importance.
    Second, cutoff point for each criterion is established.
    Finally (in order of attribute importance) brands are eliminated if they
    fail to meet or exceed the cutoff.

* __Lexicographic Decision Rule__  
    User ranks the criteria in order of importance.
    Then selects item that best on the most important attribute.

    If two or more items tie, they are evaluated on the second most important
    attribute. This continues through the attributes until on item outperforms
    the others.

* __Compensatory Decision Rule__  
    States that the item that rates highest on the sum of the users judgements
    of the relevant evaluative criteria will be chosen.

*Very much inspired by `Marketing 334 Consumer Behavior Chap016TR.ppt`*


--------------------------------------------------------------------------------


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
            { 'source': 'filesystem.basename_prefix',
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

* There are more cases like the above that should be thought about.
  A common case is the slight modification to the current file name.
  Original file name:
    ```
    2017-06-20_00-49-56 Working on autonameow.png
    ```
  Desired file name:
    ```
    2017-06-20T004956 Working on autonameow.png
    ```
  How should this be specified in the configuration?
  A simple alternative is to specify the filename analyzer as the source.
  The `DATETIME_FORMAT` makes sure that the timestamp format is changed.

    ```yaml
    RULES:
    -   DATA_SOURCES:
            extension: contents.extension
            datetime: analysis.filename.{?????}
            title: filesystem.basename_prefix
        NAME_TEMPLATE: "{datetime} {title}.{extension}"
    DATETIME_FORMAT:
        datetime: '%Y-%m-%dT%H%M%S'
    ```
  But this is not configurable -- how would the filename analyzer know
  which of many possible datetime results to use?


--------------------------------------------------------------------------------


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


--------------------------------------------------------------------------------


Data Transformation
-------------------
Thoughts on interactions between data-users ("name builder", analyzers) and
data-providers (extractors, analyzers).

Data is collected by extractors and stored in the `SessionRepository`. This
data is "raw", I.E. consists of primitives and `datetime`-objects.

Some contextual metadata should be kept along with each stored data item for;

1. Conversion of "raw" data to fit a specific name template field.
    * The byte string `.jpg` could populate the `{extension}` field by
      Unicode-conversion.
    * The MIME type `image/jpeg` (Unicode string) could also be used to
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
            wrapper=coercers.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.publisher, weight=0.25),
                fields.WeightedMapping(fields.author, weight=0.01)
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
For instance, `filesystem.mime_type` could be "coerced" or converted
to some format appropriate for populating the template field `{title}`.

```
 'application/pdf'  -->  'PDF Document'
     Raw Data              Title Field
```

This specific example would probably require some kind of lookup-table or
heuristic to convert MIME-types to a equivalent human-readable "title"-like
form.  Alternatively, this conversion could simply not be permitted.


Some "raw" data will not relate to certain name template fields in any
meaningful way.  For example, `filesystem.mime_type` can not be
transformed to a format suited for populating the template field `{datetime}`.

There is no way to transform a MIME type to date/time-information in a single
step.
The only way would be to "follow" the MIME-type data to some other related data
that might contain date/time-information.


### Example Practical Application
How would template fields map to actual "raw" data extracted from
`$AUTONAMEOW_SRCROOT_DIR/tests/samplefiles/gmail.pdf`.


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
    'metadata.exiftool.SourceFile': '/Users/jonas/PycharmProjects/autonameow.git/tests/samplefiles/gmail.pdf',
    'metadata.exiftool.ExifTool:ExifToolVersion': 10.55,
    'metadata.exiftool.File:FileName': 'gmail.pdf',
    'metadata.exiftool.File:Directory': '/Users/jonas/PycharmProjects/autonameow.git/tests/samplefiles',
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
    'filesystem.basename_full': 'gmail.pdf',
    'filesystem.extension': 'pdf',
    'filesystem.basename_suffix': 'pdf',
    'filesystem.basename_prefix': 'gmail',
    'filesystem.pathname_full': '/Users/jonas/PycharmProjects/autonameow.git/tests/samplefiles',
    'filesystem.pathname_parent': 'samplefiles',
    'filesystem.mime_type': 'application/pdf',
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
| `'filesystem.abspath_full'`                     | `'/Users/jonas/PycharmProjects/autonameow.git/tests/samplefiles/gmail.pdf'` | ?                                           |
| `'filesystem.basename_full'`                    | `'gmail.pdf'`                                                        | ?                                                  |
| `'filesystem.extension'`                        | `'pdf'`                                                              | `{extension}`                                      |
| `'filesystem.basename_suffix'`                  | `'pdf'`                                                              | `{extension}`                                      |
| `'filesystem.basename_prefix'`                  | `'gmail'`                                                            | ?                                                  |
| `'filesystem.pathname_full'`                    | `'/Users/jonas/PycharmProjects/autonameow.git/tests/samplefiles'`    | ?                                                  |
| `'filesystem.pathname_parent'`                  | `'samplesfiles'`                                                     | ?                                                  |
| `'filesystem.mime_type'`                        | `'application/pdf'`                                                  | `{extension}`                                      |
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


--------------------------------------------------------------------------------


The "Resolver"
--------------
> Jonas Sjöberg, 2017-09-25.


Modified excerpt from `autonameow/core/main.py` with a lot of added
"programming by wishful thinking", but still pretty close to the actual
current code:

```python
def _perform_automagic_actions(self, current_file, rule_matcher):
    # Using the highest ranked rule
    name_template = rule_matcher.best_match.name_template

    resolver = Resolver(current_file, name_template)
    for _field, _meowuri in rule_matcher.best_match.data_sources.items():
        resolver.add_known_source(_field, _meowuri)

    if not resolver.mapped_all_template_fields():
        if self.opts.batch_mode:
            log.error('All name template placeholder fields must be '
                      'given a data source; Check the configuration!')
            self.exit_code = C.EXIT_WARNING
            return

        elif self.opts.interactive:
            cli.msg(
                'Unknown data sources: ' + ','.join(resolver.unmapped_fields())
            )
            for field in resolver.unmapped_fields():
                candidates = resolver.lookup_candidates(field)
                choice = cli.prompt_selection(
                    heading='Field "{}" candidates:'.format(field),
                    choices=candidates
                )
                if choice in candidates:
                    resolver.add_known_source(field, choice)

    resolver.collect()
    if not resolver.collected_data_for_all_fields():
        if self.opts.batch_mode:
            log.warning('Unable to populate name. Missing field data.')
            self.exit_code = C.EXIT_WARNING
            return
        elif self.opts.interactive:
            for field in resolver.missing_fields():
                candidates = resolver.lookup_candidates(field)
                choice = cli.prompt_selection(
                    heading='Field "{}" candidates:'.format(field),
                    choices=candidates
                )
                if choice in candidates:
                    resolver.add_known_source(field, choice)

    try:
        new_name = namebuilder.build(config=self.active_config,
                                     name_template=name_template,
                                     field_data_map=resolver.fields_data)
    except exceptions.NameBuilderError as e:
        log.critical('Name assembly FAILED: {!s}'.format(e))
        raise exceptions.AutonameowException

    self.do_rename(from_path=current_file.abspath,
                   new_basename=new_name,
                   dry_run=self.opts.dry_run)
```

Alternative, more wishful and optimistic version:
```python
def _perform_automagic_actions(self, current_file, rule_matcher):
    # Using the highest ranked rule
    name_template = rule_matcher.best_match.name_template

    resolver = Resolver(current_file, name_template)
    for _field, _meowuri in rule_matcher.best_match.data_sources.items():
        resolver.add_known_source(_field, _meowuri)

    if not resolver.mapped_all_template_fields():
        if self.opts.batch_mode:
            log.error('All name template placeholder fields must be '
                      'given a data source; Check the configuration!')
            self.exit_code = C.EXIT_WARNING
            return

        elif self.opts.interactive:
            cli.msg(
                'Unknown data sources: ' + ','.join(resolver.unmapped_fields())
            )
            for field in resolver.unmapped_fields():
                candidates = resolver.lookup_candidates(field)
                choice = cli.prompt_selection(
                    heading='Field "{}" candidates:'.format(field),
                    choices=candidates
                )
                if choice in candidates:
                    resolver.add_known_source(field, choice)

    resolver.collect()
    if not resolver.collected_data_for_all_fields():
        if self.opts.batch_mode:
            log.warning('Unable to populate name. Missing field data.')
            self.exit_code = C.EXIT_WARNING
            return
        elif self.opts.interactive:
            for field in resolver.missing_fields():
                candidates = resolver.lookup_candidates(field)
                choice = cli.prompt_selection(
                    heading='Field "{}" candidates:'.format(field),
                    choices=candidates
                )
                if choice in candidates:
                    resolver.add_known_source(field, choice)

    try:
        new_name = namebuilder.build(config=self.active_config,
                                     name_template=name_template,
                                     field_data_map=resolver.fields_data)
    except exceptions.NameBuilderError as e:
        log.critical('Name assembly FAILED: {!s}'.format(e))
        raise exceptions.AutonameowException

    self.do_rename(from_path=current_file.abspath,
                   new_basename=new_name,
                   dry_run=self.opts.dry_run)
```

Updated alternative, more wishful and optimistic version:

```python
def _perform_automagic_actions(self, current_file, rule_matcher):
    if rule_matcher.best_match:
        # Using the highest ranked rule
        name_template = rule_matcher.best_match.name_template
    else:
        if self.opts.batch_mode:
            log.warning('No rule matched, name template unknown.')
            self.exit_code = C.EXIT_WARNING
            return
        else:
            choice = cli.prompt_selection(
                heading='Select a name template',
                choice=rule_matcher.candidates
            )
            if choice != cli.action.ABORT:
                name_template = choice

    resolver = Resolver(current_file, name_template)
    resolver.add_known_sources(rule_matcher.best_match.data_sources)

    resolver.collect()

    if not resolver.collected_all():
        if self.opts.batch_mode:
            log.warning('Unable to populate name.')
            self.exit_code = C.EXIT_WARNING
            return
        else:
            while not resolver.collected_all():
                for unresolved in resolver.unresolved():
                    candidates = resolver.lookup_candidates(unresolved)
                    if candidates:
                        choice = cli.prompt_selection(
                            heading='Field {}'.format(unresolved.field)
                            choices=candidates
                        )
                    else:
                        choice = cli.prompt_meowuri(
                            heading='Enter a MeowURI'
                        )
                    if choice != cli.action.ABORT:
                        resolver.add_known_source(choice)

                resolver.collect()
    try:
        new_name = namebuilder.build(
            config=self.active_config,
            name_template=name_template,
            field_data_map=resolver.fields_data
        )
    except exceptions.NameBuilderError as e:
        log.critical('Name assembly FAILED: {!s}'.format(e))
        raise exceptions.AutonameowException

    self.do_rename(
        from_path=current_file.abspath,
        new_basename=new_name,
        dry_run=self.opts.dry_run
    )
```


Auto-Completion of MeowURIs
---------------------------
When in a mode that allows querying the user, choices of data using MeowURIs
should support auto-completion. Pressing `<TAB>` should display all possible
choices.

Empty prompt:
```
>
```

After pressing `<TAB>`:
```
>
  (analysis, extractor, plugin, contents, metadata, ..)
```

Entering `e` without pressing `<ENTER>`
```
> e
```

After pressing `<TAB>`:
```
> extractor
```

Entering `.` and then pressing `<TAB>`:
```
> extractor.
  (exiftool, filesystem, pypdf, tesseract, ..)
```
