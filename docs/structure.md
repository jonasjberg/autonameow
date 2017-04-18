# `autonameow` program structure

```
Copyright(c)2016-2017 Jonas Sjoberg
                      https://github.com/jonasjberg
                      jomeganas@gmail.com

Please see "LICENSE.txt" for licensing details.
```

--------------------------------------------------------------------------------


Program structure overview
==========================
This is a high level overview of the internal architecture of `autonameow`.

**TODO:** Either scrap this kind of documentation for ever, until the project
          is done *OR*.. **MAKE SURE IT IS UP TO DATE!**

Classes
-------

### class `Autonameow`
Main class to manage "autonameow" instance.
Contains the main program entry point and main function.

### class `FileObject`
Represents a file.

### class `Analysis`
Main interface to all file analyzers.
Starts a analysis, I.E. does all handling a file.

### class `AnalyzerBase`
Analysis relevant to all files, regardless of file mime type.

Tries to find information in for instance the file names, file system metadata
(modified, created, ..), etc.

#### class `ImageAnalyzer`
*(subclasses `AnalyzerBase`)*
Analysis specific to images.

#### class `PdfAnalyzer`
*(subclasses `AnalyzerBase`)*
Analysis specific to images.
Analysis specific to pdf documents.

#### class `VideoAnalyzer`
*(subclasses `AnalyzerBase`)*
Analysis specific to images.
Analysis specific to pdf documents.

#### class `TextAnalyzer`
*(subclasses `AnalyzerBase`)*
Analysis specific to images.
Analysis specific to plain text files.



