# Diagrammer
Tapestry's diagram generation system, written primarily in Python by Arthur Lafrance and Patrick Wang

## Overview
Diagrammer is a proprietary library that sits at the core of the Tapestry Lab system. Written in Python, it is used for generating diagrams based on code snippets (currently only Python is supported, but that will change in the future!). Diagrammer works by first executing the provided code snippet, and generating _bare language data_ at a set of "flags" (points in time during the code's execution). Bare language data represents information about the state of the code at each flag, and is subsequently converted into diagram data, which is displayed separately.

## Contents
Diagrammer is mostly made up of two parts: general abstract interfaces for its functionality and language-specific subsystems that implement this functionality. Currently, the only language supported is Python, so the only subsystem present is the Python subsystem. The general contents of Diagrammer consist of:

* `scene`: a language-ambiguous tool for drawing the diagrams themselves.
* `engine`: a general, language-ambiguous interface for running code and generating bare language data. It is implemented by each language-specific subsystem

Each subsystem generally consists of the following parts:

* `scene`: the language-specific implementation of the general scene layer.
* `engine`: the language-specific implementation of the Diagrammer engine system.
* Optionally, there may also be a `utils` module where utility constructs are defined.

## Still to Come
Diagrammer is constantly evolving; here is a list of some important features that have yet to be completed:

* Multi-language support: we hope to support more than just Python in the future; top candidates for Diagrammer support are Java & C/C++.
