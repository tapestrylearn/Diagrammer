# Diagrammer
Generate diagrams of Python program state at runtime

![Usage on website](https://github.com/tapestrylearn/Diagrammer/assets/20631215/1d5d551a-d347-44e0-8f29-db6f66cb7091)

## Overview
Diagrammer is a library that generates SVG diagrams of the state of Python programs at runtime; we wrote & used it to remotely execute and diagram Python programs for Tapestry (see the screenshot above).

To generate diagrams, the given Python program is first "recursively" executed (with `exec()`) to collect "bare language data" at a set of "flags" (like breakpoints in debuggers). Bare language data is a high-level, Python-specific representation of the state of the program at each flag, which determines the elements of the diagram and their content, which is displayed separately in a language-agnostic way (see **"Architecture"** below).

For example, every variable present in the bare language data would get one square, while each primitive value would get a circle, and so on, as in the screenshot above -- bare language data reports the language-specific contents of the program's state (variables, primitive/collection values), which is mapped onto shapes in the diagram that can be displayed language-agnostically.

## Architecture
Diagrammer has two components: scenes and engines. Scenes represent the diagram itself, and engines are responsible for running code and spitting out bare language data. Each component provides a language-agnostic interface that target languages specialize to implement their own diagram generation.

The language-agnostic scene interface (the top-level `scene` module) is specified in terms of shapes that may be present in the diagram. Each language provides language-specific constructs that override these base shapes to map them onto language concepts (e.g. in Python variables are represented by squares, so Python's variable concept overrides the top-level square concept). This allows the actual SVG rendering of the entire diagram to be shared across all languages by separating language-specific concepts from their underlying visualization in the diagram.

The language-agnostic engine interface (the top-level `core.engine` module) is a very thin contract that each language-specific engine implementation must adhere too; basically, they just have to output bare language data. Each language-specific implementation sources that bare language data in its own way: the Python engine uses `exec()` to run the client program, while a hypothetical C or C++ engine might invoke `clang` in a child process.

We only implemented a Python Diagrammer engine, but in theory this architecture could've supported implementations for pretty much any other language we wanted.

## Fun Stuff

In implementing this system we made use of some ungodly Python tricks, including:
* [`ModuleProxy`](https://github.com/tapestrylearn/Diagrammer/blob/dfb1fda7ad013b79da7d8923fb1bea44db4b7f95/diagrammer/python/engine.py#L8): A read-only "proxy" for a Python module
  * Creating fake modules as read-only proxies [in Python directly](https://github.com/tapestrylearn/Diagrammer/blob/dfb1fda7ad013b79da7d8923fb1bea44db4b7f95/diagrammer/python/engine.py#L131), and [injecting calls](https://github.com/tapestrylearn/Diagrammer/blob/dfb1fda7ad013b79da7d8923fb1bea44db4b7f95/diagrammer/python/engine.py#L168) to functions in those modules later on (as plain strings)
* [`BlockedConstruct`](https://github.com/tapestrylearn/Diagrammer/blob/dfb1fda7ad013b79da7d8923fb1bea44db4b7f95/diagrammer/python/engine.py#L37): A universal callable that yells at you loudly for doing something illegal
* Generous use of "recursive" execution of Python code with `exec()` and `eval()`

It was also surprisingly difficult to come up with the right conceptual framework for positioning elements in the diagram: finding the right balance between positional rigidity (to avoid really wonky diagrams) and fluidity (to give ourselves room to make things look nice) ended up being very difficult. We also got a kick out of naming what we came up with `gps`.
