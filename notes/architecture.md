Notes on possible changes to the overall architecture.


## Module hierarchy

- autonameow
    - analyzers
    - core
    - extractors
    - plugins


## Class hierarchy
What are the advantages of multi-level inheritance?

Would it be better to think about inheritance hierarchies at a later time,
with more information on how the extractors/analyzers will actually be used?

### Analyzers
Current inheritance:

- AbstractAnalyzer
    - FilenameAnalyzer
    - FilesystemAnalyzer
    - ImageAnalyzer
    - PdfAnalyzer
    - TextAnalyzer
    - VideoAnalyzer

### Extractors
Proposed inheritance:

- Extractor
    - MetadataExtractor
        - ExiftoolMetadataExtractor
        - PyPDFMetadataExtractor
    - *TextExtractor*
        - *PdfToTextExtractor*
        - *PyPDFTextExtractor*
        - *PyTesseractTextExtractor*


* Why use inheritance?

    * Provides means for getting extractors suited for a given file. 

        ```python
        for extractor in available_extractors:
            if extractor.handles(file_mime_type):
                enqueue(extractor)
        queue.run()
        ```

        Alternatively:
        ```python
        extractors = suitable_extractors(file_mime_type)
        enqueue(extractors)
        queue.run()
        ```

    * Reduce duplicate code, etc..


### Analyzers vs. Extractors
If extractors were to handle low-level data extraction from various formats,
while analyzers work with the extracted data at a higher level. The distinction
between for example a PDF ebook and a PDF of a scanned bill , should be made at
the analyzer-level.

How would the current analyzer code be changed?

Would it make sense to use inheritance?

For instance:

- Analyzer base class
    - DocumentAnalyzer
        - BookAnalyzer
        - BillAnalyzer

This kind of abstraction might not be a good solution..


## Moving to separate analyzers and extractors
The user could configure file rule to fetch specific extracted data fields.
These would be fixed and only processed in the most basic way.

The *file rule* would specify a *data source* like:
`extracted_data.filesystem.basename`

Alternatively, the user could set up the rule to use analyzer data, for instance:
`analysis_results.title`

This would use a "most likely" title from whatever source.
Suitable analyzers for the given file would be enqueued and executed.
The specific analyzer would decide which title, or list of candidates to use.

