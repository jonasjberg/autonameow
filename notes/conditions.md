`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Rule Conditions
===============
Notes on Conditions in the Rules defined in the Configuration.

#### Revisions
* 2017-06-27 --- `jonasjberg` Initial
* 2017-06-28 --- `jonasjberg` Added alternative "flat" config syntax
* 2017-06-30 --- `jonasjberg` The "flattened" config syntax is now default.
* 2017-09-23 --- `jonasjberg` Merged with `2017-07-07_raw-conditions.md`
* 2017-12-12 --- `jonasjberg` Add notes on rule evaluation details.
* 2017-12-13 --- `jonasjberg` Start writing possible expression syntax.


2017-12-13 --- Expression Syntax
================================
Some kind of initial syntax is required in order to properly implement rule
condition expressions as per `[TD0015]`.

Old use-case examples, with possible configuration entries that satisfy
the requirement;

* __Is some metadata field available?__  
  Examples:
    * *Does the file metadata contain `EXIF:DateTimeOriginal`?*
        * Rule condition:
            ```yaml
            extractor.metadata.exiftool.EXIF:DateTimeOriginal: DEFINED
            ```
    * *Does the file metadata contain __any__ creation date? (`DateCreated`)*
        * Rule condition:
            ```yaml
            generic.metadata.date_created: DEFINED
            ```

* __Is some date/time-data within a range?__  
  Examples:
    * *Was `EXIF:DateTimeOriginal` more recent than 2017-05-04 and older than 2017-06-27?*
        * Rule condition:
            ```yaml
            extractor.metadata.exiftool.EXIF:DateTimeOriginal: 2017-05-04 > X > 2017-06-27
            ```
    * *Was `DateCreated` at or after 2017-06-27?*
        * Rule condition:
            ```yaml
            extractor.metadata.exiftool.EXIF:DateTimeOriginal: X >= 2017-06-27
            ```
    * *Was `DateCreated` before 2017-05-04?*
        * Rule condition:
            ```yaml
            extractor.metadata.exiftool.EXIF:DateTimeOriginal: X < 2017-05-04
            ```
    * ~~*Was `DateCreated` before `DateModified`?*~~
        * Rule condition:
            ```yaml
            generic.metadata.date_created: < generic.metadata.date_modified
            ```
    * ~~*Was `DateCreated` before `DateModified` and after 2017-06-27?*~~
        * Rule condition:
            ```yaml
            generic.metadata.date_created: X < generic.metadata.date_modified ???
            ```

It is pretty clear that the current format using the YAML-version of a
dictionary does not work very well for some of the above expressions..



2017-12-12 --- Reworking Rule Evaluation
========================================
Notes on reworking the messy rule evaluation and adding better "diagnostics".


Current, shorter listing
------------------------
```
Rule #001 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
Rule #002 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
Rule #003 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
Rule #004 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
Rule #005 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
```


Adding Detailed Listing of Rule Evaluation
------------------------------------------
As per TODO-list entry "`[TD0135]` Add option to display rule matching
information."


Mock-up of possible output format:

```
Rule #001 [RULE DESCRIPTION] (3 conditions)

PASSED

  - extractor.filesystem.xplat.basename_full
    Expression          'Untitled.mov'
    Evaluated Data      'Untitled.mov'

  - extractor.filesystem.xplat.mime_type
    Expression         'video/quicktime'
    Evaluated Data     'video/quicktime'

FAILED

  - extractor.filesystem.xplat.pathname_full
    Expression         '/Users/jonas/Desktop'
    Evaluated Data     '/home/jonas/whatever'

Exact: Yes  Score: 0.0  Weight: 0.0  Bias: 0.0
```

Alternative mock-up:
```
Rule #001 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]

PASSED  extractor.filesystem.xplat.basename_full
        Expr:  'Untitled.mov'
        Data:  'Untitled.mov'
PASSED  extractor.filesystem.xplat.mime_type
        Expr:  'video/quicktime'
        Data:  'video/quicktime'
FAILED  extractor.filesystem.xplat.pathname_full
        Expr:  '/Users/jonas/Desktop'
        Data:  '/home/jonas/whatever'

Rule #002 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
Rule #003 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
Rule #004 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
Rule #005 (Exact: Yes/No  Score: 0.0  Weight: 0.0  Bias: 0.0)  [RULE DESCRIPTION]
```


Would probably be nice to display additional detailed of possible
transformations of the expression and evaluated data, like expanding
`~` in paths before matching a regular expression, etc.


2017-07-07 --- Validating Rule Conditions
=========================================
The "raw" file rule conditions from YAML configuration should be validated.


Examples:

```python
raw_conditions = {
    'mime_type' = 'application/pdf'
    'filesystem.basename' = 'gmail.pdf'
    'filesystem.extension' = 'pdf'
}
```

```python
raw_conditions = {
    'mime_type' = 'image/jpeg'
    'filesystem.basename' = 'DCIM*'
    'filesystem.extension' = 'jpg'
    'filesystem.pathname' = '~/Pictures/incoming'
    'metadata.exiftool.EXIF:DateTimeOriginal' = 'Defined'
}
```

```python
raw_conditions = {
    'mime_type' = 'application/epub+zip'
    'filesystem.basename' = '.*'
    'filesystem.extension' = 'epub'
    'filesystem.pathname' = '.*'
    'metadata.exiftool.XMP-dc:Creator' = 'Defined'
}
```

Possible solutions:

1. Encapsulate each condition in a class instance
    * The class could validate the data at instantiation.
    * The condition field ("query string") `mime_type` is to be
      validated by the `MimeTypeConfigFieldParser`, while the
      `filesystem.basename` condition should be checked by the
      `RegexConfigFieldParser`.


2017-06-27
==========
Current format for a file rule in the configuration file:

```yaml
-   CONDITIONS:
        mime_type: image/jpeg
        filesystem.basename: smulan.jpg
    DATA_SOURCES:
        datetime: metadata.exiftool.EXIF:DateTimeOriginal
        description: plugin.microsoft_vision.caption
        extension: filesystem.extension
    NAME_TEMPLATE: '{datetime} {description}.{extension}'
    description: test_files smulan.jpg
    exact_match: true
    weight: 1
```


The `CONDITIONS` section should be redesigned.

### Wishlist:
Ability to specify conditionals;

* __Is some metadata field available?__  
  Examples:
    * *Does the file metadata contain `EXIF:DateTimeOriginal`?*
    * *Does the file metadata contain __any__ creation date? (`DateCreated`)*

* __Is some date/time-data within a range?__  
  Examples:
    * *Was `EXIF:DateTimeOriginal` more recent than 2017-05-04 and older than 2017-06-27?*
    * *Was `DateCreated` after 2017-06-27?*
    * *Was `DateCreated` before 2017-05-04?*
    * ~~*Was `DateCreated` before `DateModified`?*~~
    * ~~*Was `DateCreated` before `DateModified` and after 2017-06-27?*~~

* __Does the contents match some criteria? (text matches regex, etc.)?__  
  Example: *Does the first page text match this regular expression?*


### Proposed New Format
Possible new format for a file rule in the configuration file:

```yaml
-   CONDITIONS:
        mime_type: image/jpeg
        filesystem.basename: DCIM.*
        filesystem.extension: jpg
        metadata.exiftool.EXIF:DateTimeOriginal: Defined
        metadata.exiftool.EXIF:DateTimeOriginal: > 2017-05-04
        metadata.exiftool.EXIF:DateTimeOriginal: < 2017-06-27
    DATA_SOURCES:
        datetime: metadata.exiftool.EXIF:DateTimeOriginal
        description: plugin.microsoft_vision.caption
        extension: filesystem.extension
    NAME_TEMPLATE: '{datetime} {description}.{extension}'
    description: Photos taken between 2017-05-04 and 2017-06-27
    exact_match: true
    weight: 1
```

This rule would only apply for files with base name `smulan.jpg`, extraction
results must contain exiftool metadata field `EXIF:DateTimeOriginal` and this
date must be after *2017-05-04* and prior to *2017-06-27*.



Another hypothetical file rule using unimplemented features:

```yaml
-   CONDITIONS:
        mime_type: application/pdf
        contents.textual.raw_text: ^Gibson[ _-]?Rules.*?$
    DATA_SOURCES:
        author: book_analyzer.isbn.author
        date: [metadata.exiftool.PDF:CreateDate, book_analyzer.isbn.date]
        description: book_analyzer.isbn.title
        extension: pdf
        title: book_analyzer.isbn.title
    NAME_TEMPLATE: '{date} {description} - {author}.{extension}'
    description: Engineering textbook written by Gibson
    exact_match: true
    weight: 1
```

