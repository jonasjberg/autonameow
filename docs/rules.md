`autonameow` data formats
=========================

```
Copyright(c)2016-2017 Jonas Sjoberg
                      https://github.com/jonasjberg
                      jomeganas@gmail.com

Please see "LICENSE.txt" for licensing details.
```

--------------------------------------------------------------------------------


Available Fields
================

* Filename
    * Pathname
    * Basename
    * Extension
* Contents
    * MIME type
    * Text
        * `pages` (list of pages)
            * ( Page 1 )
                * `page_number`
                * `contents` (list of text lines)
            * ( Page n )
                * `page_number`
                * `contents` (list of text lines)
        * Number of pages
        * EXIF Metadata
    * Image
        * Text 
            * `contents` (list of text lines)
        * EXIF metadata
    * Video
        * ..
        * ..
* File System
    * Create date
    * Modify date
    * Access date
    * Permissions


Rule Configuration File Syntax
==============================

```
- ExactMatch: True
- Weight: 0.2
- Filename
    - Pathname: "~/today"
    - Basename: "*screenshot*"
    - Extension: *.png"
- Contents
    - Mime type: "image/png"
```

### 

| Description               | Current Pathname        | Current Basename             | Extension | Contents |
|---------------------------|-------------------------|------------------------------|-----------|----------|
| Websites printed to html  | `~/Dropbox/incoming`    | `[URL] [YYYY-MM-DD] [title]` | `pdf`     | First line of all pages matches: `4/29/2017 [title]` |



### Websites saved to PDF from browsers "Print to PDF..":

* Pathname: `~/Dropbox/incoming`
* Current Basename: `[URL] [YYYY-MM-DD] [title]`
* Extension: `pdf`
* Contents:
    * First line of all pages match: `4/29/2017 [\W+] [title]`
    * Last line of all pages match: `[URL] [current_page_number]/[number_pages]`


