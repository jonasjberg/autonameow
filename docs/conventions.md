`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Conventions used by `autonameow`
================================
Various conventions used in the `autonameow` project.


File/path-names
----------------
The following naming conventions are used in the source code, originating
primarily from the `FileObject` class.


Given the path `/home/gibson/foo.txt`:

```
Name               Value
=================================================
abspath          : /home/gibson/Documents/foo.txt
pathname         : /home/gibson/Documents
pathparent       :              Documents
filename         :                        foo.txt
basename_prefix  :                        foo
basename_suffix  :                            txt
```


The most obvious deviation from de-facto standards is the treatment of file
extensions.


Given the path `/home/gibson/foo.tar.gz`:

```
Name               Value
====================================================
abspath          : /home/gibson/Documents/foo.tar.gz
pathname         : /home/gibson/Documents
pathparent       :              Documents
filename         :                        foo.tar.gz
basename_prefix  :                        foo
basename_suffix  :                            tar.gz
```



<!-- TODO: Document naming convention for mapping converting extensions to MIME-types. -->
