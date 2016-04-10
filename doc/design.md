`autonameow` -- Design Document
================================================================================


Basic program functionality
===========================
Find suitable file names from a set of rules.

A set of rules dictates what is a "suitable file name" -- **target file name**.

The target file name is defined as a number of ordered fields.

#### Example target: `[timestamp] [title] [author]`

The program is to fill out these fields by reading in a bunch of data
from/about the file, which is then analyzed and ranked by probability, as
defined by some set of rules.


High-level logic
----------------
Breakdown of what needs to happen to automatically rename a file:

1. Read data from file:

    * File **name**
        * `seemingly giant cat in dollhouse.jpg`

    * File **contents**
        * Plain text extracted from contents.
        * Extraction technique would be specfic to file type;
          `OCR` for images, etc.

    * File **metadata**
        * Plain text extracted from metadata.
        * Metadata type and extraction technique would be specfic to file type;
          "media" often have `EXIF` data, pdf documents, etc.

2. Evaluate the results.

    * Sort
        * How?

    * Filter
        * How?

3. Construct a new file name from the data.

4. Rename the file.



Example
-------

### Read data from file
Reading from file `~/Downloads/DSCN9659.jpg`

* **File name**
  `DSCN9659.jpg` (basename?)

* **Contents**
  Might be able to extract information from an image? Image similarity search?
  TODO: Investigate .. Just skip reading image file contents for now.

* **Metadata**
  Extract image exif information by some means.
  Probably won't need to use more than one program/library to do it.
  Below two examples should be checked for duplicate data.


```
> $ exif ~/Downloads/DSCN9659.jpg
EXIF tags in '/home/spock/temp/smf/img/DSCN9659.jpg' ('Intel' byte order):
--------------------+----------------------------------------------------------
Tag                 |Value
--------------------+----------------------------------------------------------
Image Description   |
Manufacturer        |NIKON
Model               |E775
Orientation         |Top-left
X-Resolution        |300
Y-Resolution        |300
Resolution Unit     |Inch
Software            |E775v1.4u
Date and Time       |0000:00:00 00:00:00
YCbCr Positioning   |Co-sited
Exposure Time       |1/41 sec.
F-Number            |f/3,0
Exposure Program    |Normal program
ISO Speed Ratings   |100
Exif Version        |Exif Version 2.1
Date and Time (Origi|0000:00:00 00:00:00
Date and Time (Digit|0000:00:00 00:00:00
Components Configura|Y Cb Cr -
Compressed Bits per | 3
Exposure Bias       |0,00 EV
Maximum Aperture Val|3,50 EV (f/3,4)
Metering Mode       |Pattern
Light Source        |Unknown
Flash               |Flash did not fire
Focal Length        |7,1 mm
Maker Note          |674 bytes undefined data
User Comment        |
FlashPixVersion     |FlashPix Version 1.0
Color Space         |sRGB
Pixel X Dimension   |1600
Pixel Y Dimension   |1200
File Source         |DSC
Scene Type          |Directly photographed
Interoperability Ind|R98
Interoperability Ver|0100
--------------------+----------------------------------------------------------
```

```
> $ exiftool ~/Downloads/DSCN9659.jpg
ExifTool Version Number         : 10.00
File Name                       : DSCN9659.jpg
Directory                       : /home/spock/Downloads
File Size                       : 108 kB
File Modification Date/Time     : 2016:03:21 17:44:58+01:00
File Access Date/Time           : 2016:03:21 17:44:58+01:00
File Inode Change Date/Time     : 2016:03:21 17:44:58+01:00
File Permissions                : rw-rw-r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.02
Ocad Revision                   : 14797
Exif Byte Order                 : Little-endian (Intel, II)
Image Description               :
Make                            : NIKON
Camera Model Name               : E775
Orientation                     : Horizontal (normal)
X Resolution                    : 300
Y Resolution                    : 300
Resolution Unit                 : inches
Software                        : E775v1.4u
Modify Date                     : 0000:00:00 00:00:00
Y Cb Cr Positioning             : Co-sited
Exposure Time                   : 1/41
F Number                        : 3.0
Exposure Program                : Program AE
ISO                             : 100
Exif Version                    : 0210
Date/Time Original              : 0000:00:00 00:00:00
Create Date                     : 0000:00:00 00:00:00
Components Configuration        : Y, Cb, Cr, -
Compressed Bits Per Pixel       : 3
Exposure Compensation           : 0
Max Aperture Value              : 3.4
Metering Mode                   : Multi-segment
Light Source                    : Unknown
Flash                           : No Flash
Focal Length                    : 7.1 mm
Warning                         : [minor] Possibly incorrect maker notes offsets (fix by -288?)
Maker Note Version              : 1.00
Color Mode                      :
Quality                         :
White Balance                   :
Sharpness                       :
Focus Mode                      :
Flash Setting                   :
ISO Selection                   : .'
Image Adjustment                : .'
Auxiliary Lens                  :
Manual Focus Distance           : 0.0606
Digital Zoom                    : 0.0139
AF Area Mode                    : Single Area
AF Point                        : Center
AF Points In Focus              : (none)
Scene Mode                      : .
Data Dump                       : (Binary data 122 bytes, use -b option to extract)
User Comment                    :
Flashpix Version                : 0100
Color Space                     : sRGB
Exif Image Width                : 1600
Exif Image Height               : 1200
Interoperability Index          : R98 - DCF basic file (sRGB)
Interoperability Version        : 0100
File Source                     : Digital Camera
Scene Type                      : Directly photographed
Image Width                     : 800
Image Height                    : 600
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:2:2 (2 1)
Aperture                        : 3.0
Image Size                      : 800x600
Megapixels                      : 0.480
Shutter Speed                   : 1/41
Focal Length                    : 7.1 mm
Light Value                     : 8.5
```




Naming convention
================================================================================

The naming convention is a configurable pattern of fields that is used for
constructing new file names.

File type determines which naming pattern is used.
Different naming patterns apply to different file types, should be
user configurable.

In the examples below, ' _ ' is a customizable field separator.



The terms used in the examples are defined as follows.

+----------+-----------------------------+--------------+
| **Term** | **Field description**       | **Example**  |
+==========+=============================+==============+
| ` _ `    | (top-level) field separator | `_`,` `,`-`  |
| `[date]` | ISO-8601 style date         | `2016-02-29` |
| `[time]` | ISO-8601 style time         | `13-24-34`   |
| `[ext]`  | file extension              | `jpg`,`txt`  |
+----------+-----------------------------+--------------+



Definition of terms


Photos
------
Photo images (schematics, etc excluded?) should match the pattern:

    [date] _ [time] _ [description/name] . [ext]
                          (optional)       (jpg)



Pdf books
---------
File names are to match the pattern:

    [title] _ [edition] _ [author(s) last name] _ [publisher] _ [year] . [ext]
              (optional)                                                 (jpg)

