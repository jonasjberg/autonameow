`autonameow` data formats
=========================

```
Copyright(c)2016-2017 Jonas Sjoberg
                      https://github.com/jonasjberg
                      jomeganas@gmail.com

Please see "LICENSE.txt" for licensing details.
```

--------------------------------------------------------------------------------


Current format of the analysis results data structure, 
`core.analyze.analysis.Analysis.results`. 

autonameow was executed with the command;
`/Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6 /Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/autonameow/__main__.py --debug --list-all -- /Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/test_files/2010-01-31_161251.jpg`j


```python
results = {
        "datetime": {
                "ImageAnalyzer": [
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "datetimeoriginal",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "datetimedigitized",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "datetime",
                                "weight": 0.75
                        }
                ],
                "FilesystemAnalyzer": [
                        {
                                "value": "datetime.datetime(2016, 2, 24, 15, 8, 34)",
                                "source": "modified",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2017, 5, 1, 16, 12, 40)",
                                "source": "created",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2017, 5, 5, 0, 1, 50)",
                                "source": "accessed",
                                "weight": 0.25
                        }
                ],
                "FilenameAnalyzer": [
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "very_special_case",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 0, 0)",
                                "source": "regex_search",
                                "weight": 0.25
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "bruteforce_search",
                                "weight": 0.1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 0, 0)",
                                "source": "bruteforce_search",
                                "weight": 0.1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 1, 0, 0)",
                                "source": "bruteforce_search",
                                "weight": 0.1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 1, 0, 0)",
                                "source": "bruteforce_search",
                                "weight": 0.1
                        }
                ]
        },
        "publisher": {
                "ImageAnalyzer": null,
                "FilesystemAnalyzer": null,
                "FilenameAnalyzer": null
        },
        "title": {
                "ImageAnalyzer": null,
                "FilesystemAnalyzer": null,
                "FilenameAnalyzer": []
        },
        "tags": {
                "ImageAnalyzer": null,
                "FilesystemAnalyzer": null,
                "FilenameAnalyzer": []
        },
        "author": {
                "ImageAnalyzer": null,
                "FilesystemAnalyzer": null,
                "FilenameAnalyzer": null
        }
}
```    