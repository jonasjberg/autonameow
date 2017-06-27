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

* __Some metadata field is available?__  
  *Does the file metadata contain `EXIF:DateTimeOriginal`?*

* __Some date/time-data lies within a range?__
  *Is `EXIF:DateTimeOriginal` more recent than 2017-05-04 and older than 2017-06-27?*

* __Test contents (text matches regex, etc.)?__


### Proposed New Format 
Possible new format for a file rule in the configuration file:

```yaml
-   CONDITIONS:
        contents:
            mime_type: image/jpeg
        filesystem:
            basename: smulan.jpg
        metadata:
            exiftool.EXIF:DateTimeOriginal: Defined
            exiftool.EXIF:DateTimeOriginal: > 2017-05-04
            exiftool.EXIF:DateTimeOriginal: < 2017-06-27
    DATA_SOURCES:
        datetime: metadata.exiftool.EXIF:DateTimeOriginal
        description: plugin.microsoft_vision.caption
        extension: filesystem.basename.extension
    NAME_FORMAT: '{datetime} {description}.{extension}'
    description: test_files smulan.jpg
    exact_match: true
    weight: 1
```

This rule would only apply for files with base name `smulan.jpg`, the exiftool
metadata field `EXIF:DateTimeOriginal` must be available and the date must be
after 2017-05-04 and prior to 2017-06-27.

