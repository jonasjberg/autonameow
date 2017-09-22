Notes on Configuration File Rule Conditions
===========================================
Jonas Sjöberg, 2017-06-27.  

* Revised 2017-06-28 -- Added alternative "flat" configuration syntax.
* Revised 2017-06-30 -- The "flattened" configuration syntax is now default.
* Revised 2017-09-23 -- Merged with `2017-07-07_raw-conditions.md`


Current format for a file rule in the configuration file:

```yaml
-   CONDITIONS:
        contents.mime_type: image/jpeg
        filesystem.basename: smulan.jpg
    DATA_SOURCES:
        datetime: metadata.exiftool.EXIF:DateTimeOriginal
        description: plugin.microsoft_vision.caption
        extension: filesystem.basename.extension
    NAME_FORMAT: '{datetime} {description}.{extension}'
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
        contents.mime_type: image/jpeg
        filesystem.basename: DCIM.*
        filesystem.extension: jpg
        metadata.exiftool.EXIF:DateTimeOriginal: Defined
        metadata.exiftool.EXIF:DateTimeOriginal: > 2017-05-04
        metadata.exiftool.EXIF:DateTimeOriginal: < 2017-06-27
    DATA_SOURCES:
        datetime: metadata.exiftool.EXIF:DateTimeOriginal
        description: plugin.microsoft_vision.caption
        extension: filesystem.basename.extension
    NAME_FORMAT: '{datetime} {description}.{extension}'
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
        contents.mime_type: application/pdf
        contents.textual.raw_text: ^Gibson[ _-]?Rules.*?$
    DATA_SOURCES:
        author: book_analyzer.isbn.author
        date: [metadata.exiftool.PDF:CreateDate, book_analyzer.isbn.date]
        description: book_analyzer.isbn.title
        extension: pdf
        title: book_analyzer.isbn.title
    NAME_FORMAT: '{date} {description} - {author}.{extension}'
    description: Engineering textbook written by Gibson
    exact_match: true
    weight: 1
```



2017-07-07 --- Validating Rule Conditions
=========================================
The "raw" file rule conditions from YAML configuration should be validated.


Examples:

```python
raw_conditions = {
    'contents.mime_type' = 'application/pdf'
    'filesystem.basename' = 'gmail.pdf'
    'filesystem.extension' = 'pdf'
}
```

```python
raw_conditions = {
    'contents.mime_type' = 'image/jpeg'
    'filesystem.basename' = 'DCIM*'
    'filesystem.extension' = 'jpg'
    'filesystem.pathname' = '~/Pictures/incoming'
    'metadata.exiftool.EXIF:DateTimeOriginal' = 'Defined'
}
```

```python
raw_conditions = {
    'contents.mime_type' = 'application/epub+zip'
    'filesystem.basename' = '.*'
    'filesystem.extension' = 'epub'
    'filesystem.pathname' = '.*'
    'metadata.exiftool.XMP-dc:Creator' = 'Defined'
}
```

Possible solutions:

1. Encapsulate each condition in a class instance
    * The class could validate the data at instantiation.
    * The condition field ("query string") `contents.mime_type` is to be
      validated by the `MimeTypeConfigFieldParser`, while the
      `filesystem.basename` condition should be checked by the
      `RegexConfigFieldParser`.
