`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Notes on Unstructured Text
==========================
Various notes and ideas on extracting information from unstructured text.

#### Revisions
* 2018-06-12 --- `jonasjberg` Initial



Text Segmentation and Named Entity Recognition
----------------------------------------------

__Look into relationship between "named entity recognition" and "text segmentation".__


Given this unstructured text:

```
The Paperboy, The Wallet,
and The Law Of Demeter
By David Bock
dbock@fgm.com

Introduction
When I was in college, I had a professor who stated that every programmer had a 'bag of tricks' -
solutions that we tend to use over and over again because in our own personal experience, they ..
```

We want to find these named entities:

| Field  | Value                                            |
| ------ | ------------------------------------------------ |
| Author | David Bock                                       |
| E-mail | dbock@fgm.com                                    |
| Title  | The Paperboy, The Wallet, and The Law Of Demeter |



Possible high-level approaches:

* Rule-based matching with fixed patterns, similar to `guessit`
* Statistical parsing
