Notes on Configuration File Rule Conditions
===========================================
Jonas Sjöberg, 2017-06-27.


Current format for a file rule in the configuration file:

```yaml
-   CONDITIONS:
        contents:
            mime_type: image/jpeg
        filesystem:
            basename: smulan.jpg
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

* __Is some metadata field is available?__  
  Example: *Does the file metadata contain `EXIF:DateTimeOriginal`?*

* __Is some date/time-data within a range?__  
  Example: *Is `EXIF:DateTimeOriginal` more recent than 2017-05-04 and older than 2017-06-27?*

* __Does the contents match some criteria? (text matches regex, etc.)?__  
  Example: *Does the first page text match this regular expression?*


### Proposed New Format
Possible new format for a file rule in the configuration file:

```yaml
-   CONDITIONS:
        contents:
            mime_type: image/jpeg
        filesystem:
            basename: DCIM.*
            extension: jpg
        metadata:
            exiftool.EXIF:DateTimeOriginal: Defined
            exiftool.EXIF:DateTimeOriginal: > 2017-05-04
            exiftool.EXIF:DateTimeOriginal: < 2017-06-27
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
        contents:
            mime_type: application/pdf
            textual.raw_text: ^Gibson[ _-]?Rules.*?$
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
