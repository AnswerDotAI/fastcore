# fastcore

fastcore adds to Python features inspired by other languages, like mixins from Ruby, and currying, binding, and more from Haskell. It also adds some "missing features" and clean up some rough edges in the Python standard library, such as simplifying parallel processing, and bringing ideas from NumPy over to Python's list type.

Here are some tips on using fastcore:

- **Liberal imports**: Utilize `from fastcore.module import *` freely. The library is designed for safe wildcard imports.
- **Enhanced list operations**: Substitute `list` with `L`. This provides advanced indexing, method chaining, and additional functionality while maintaining list-like behavior.
- **Extend existing classes**: Apply the `@patch` decorator to add methods to classes, including built-ins, without subclassing. This enables more flexible code organization.
- **Streamline class initialization**: In `__init__` methods, use `store_attr()` to efficiently set multiple attributes, reducing repetitive assignment code.
- **Explicit keyword arguments**: Apply the `delegates` decorator to functions to replace `**kwargs` with specific parameters, enhancing IDE support and documentation.
- **Optimize parallel execution**: Leverage fastcore's enhanced `ThreadPoolExecutor` and `ProcessPoolExecutor` for simplified concurrent processing.
- **Expressive testing**: Prefer fastcore's testing functions like `test_eq`, `test_ne`, `test_close` for more readable and informative test assertions.
- **Advanced file operations**: Use the extended `Path` class, which adds methods like `ls()`, `read_json()`, and others to `pathlib.Path`.
- **Flexible data structures**: Convert between dictionaries and attribute-access objects using `dict2obj` and `obj2dict` for more intuitive data handling.
- **Functional programming paradigms**: Utilize tools like `compose`, `maps`, and `filter_ex` to write more functional-style Python code.
- **Documentation**: Use `docments` where possible to document parameters of functions and methods.
- **Time-aware caching**: Apply the `timed_cache` decorator to add time-based expiration to the standard `lru_cache` functionality.
- **Simplified CLI creation**: Use fastcore's console script utilities to easily transform Python functions into command-line interfaces.

## Tutorials

- [Fastcore Quick Tour](https://fastcore.fast.ai/tour.html.md): A quick tour of a few higlights from fastcore.
- [Blog Post](https://gist.githubusercontent.com/hamelsmu/ea9e0519d9a94a4203bcc36043eb01c5/raw/6c0c96a2823d67aecc103206d6ab21c05dcd520a/fastcore:_an_underrated_python_library.md): A tour of some of the features of fastcore.

## API

- [API List](https://fastcore.fast.ai/apilist.txt): A succint list of all functions and methods in fastcore.

## Optional

- [fastcore.test](https://fastcore.fast.ai/test.html.md): Simple testing functions
- [fastcore.basics](https://fastcore.fast.ai/basics.html.md): Basic functionality used in the fastai library.
- [fastcore.foundation](https://fastcore.fast.ai/foundation.html.md): The L class and helpers for it
- [fastcore.xtras](https://fastcore.fast.ai/xtras.html.md): Utility functions used in the fastai library
- [fastcore.parallel](https://fastcore.fast.ai/parallel.html.md):parallel processing
- [fastcore.net](https://fastcore.fast.ai/net.html.md): testing utilities
- [fastcore.docments](https://fastcore.fast.ai/docments.html.md): documentation utilities
- [fastcore.meta](https://fastcore.fast.ai/meta.html.md): metaclasses
- [fastcore.script](https://fastcore.fast.ai/script.html.md): CLI script utilities
- [fastcore.xdg](https://fastcore.fast.ai/xdg.html.md): XDG Base Directory Specification helpers.
- [fastcore.xml](https://fastcore.fast.ai/xml.html.md): concise generation of XML