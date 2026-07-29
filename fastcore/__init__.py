"""Python supercharged for fastai development

Python is a powerful, dynamic language. Rather than bake everything into the language, it lets the programmer customize it to make it work for them. `fastcore` uses this flexibility to add to Python features inspired by other languages we've loved, mixins from Ruby, and currying, binding, and more from Haskell. It also adds some "missing features" and cleans up some rough edges in the Python standard library, such as simplifying parallel processing, and bringing ideas from NumPy over to Python's `list` type.

Here are some tips on using fastcore:

- **Liberal imports**: Use `from fastcore.module import *` freely. The library is designed for safe wildcard imports.
- **Enhanced list operations**: Substitute `list` with `L`. This provides advanced indexing, method chaining, and additional functionality while maintaining list-like behavior.
- **Extend existing classes**: Apply the `@patch` decorator to add methods to classes, including built-ins, without subclassing.
- **Streamline class initialization**: In `__init__` methods, use `store_attr()` to efficiently set multiple attributes, reducing repetitive assignment code.
- **Explicit keyword arguments**: Apply the `delegates` decorator to functions to replace `**kwargs` with specific parameters, enhancing IDE support and documentation.
- **Optimize parallel execution**: Use fastcore's enhanced `ThreadPoolExecutor` and `ProcessPoolExecutor` for simplified concurrent processing.
- **Expressive testing**: Prefer fastcore's testing functions like `test_eq`, `test_ne`, `test_close` for more readable and informative test assertions.
- **Advanced file operations**: Use the extended `Path` class, which adds methods like `ls()`, `read_json()`, and others to `pathlib.Path`.
- **Flexible data structures**: Convert between dictionaries and attribute-access objects using `dict2obj` and `obj2dict` for more intuitive data handling.
- **Functional programming paradigms**: Use tools like `compose`, `maps`, and `filter_ex` to write more functional-style Python code.
- **Documentation**: Use `docments` where possible to document parameters of functions and methods.
- **Time-aware caching**: Apply the `timed_cache` decorator to add time-based expiration to the standard `lru_cache` functionality.
- **Simplified CLI creation**: Use `fastcore.script` to easily transform Python functions into command-line interfaces.

For example, `L` is a drop-in replacement for `list` with extra superpowers:

```python
x = L(1,2,3,4)
test_eq(x[[0,3]], [1,4])               # index with a collection
test_eq(x.map(lambda o:o*2), [2,4,6,8])
test_eq(x.filter(lambda o:o>2), [3,4])
x += [5]
test_eq(x.unique(), [1,2,3,4,5])
```

## Tutorials

- [Quick tour](https://fastcore.fast.ai/tour.html.md): A quick tour of a few highlights from fastcore.
- [fastcore: an underrated Python library](https://gist.githubusercontent.com/hamelsmu/ea9e0519d9a94a4203bcc36043eb01c5/raw/6c0c96a2823d67aecc103206d6ab21c05dcd520a/fastcore:_an_underrated_python_library.md): A tour of some of the features of fastcore.
- [API list](https://fastcore.fast.ai/apilist.txt): A succinct list of all functions and methods in fastcore.

Modules:

- `fastcore.aio`: Bridging async and sync code: `run_sync`, `iter_sync`, `ctx_sync`, `athreaded`, `maybe_await`, and `then`
- `fastcore.basics`: Basic functionality used in the fastai library
- `fastcore.docments`: Document parameters using comments.
- `fastcore.editskill`: Text, file, cell, and notebook editing from `fastcore.tools` and `fastcore.nbio`, plus the conventions the whole fastai editing toolkit follows. Read this before working with the editing tools in any package that shares them.
- `fastcore.foundation`: The `L` class and helpers for it
- `fastcore.meta`: Metaclasses
- `fastcore.nbio`: Reading and writing Jupyter notebooks
- `fastcore.net`: Network, HTTP, and URL functions
- `fastcore.parallel`: Threading and multiprocessing functions
- `fastcore.script`: Creates a CLI from a Python function decorated with `call_parse`.
- `fastcore.style`: Fast styling for friendly CLIs.
- `fastcore.test`: Helper functions to quickly write tests in notebooks
- `fastcore.tools`: Text and file editing primitives shared by the fastai editing tools
- `fastcore.xdg`: XDG Base Directory Specification helpers.
- `fastcore.xml`: Concise generation of XML.
- `fastcore.xtras`: Utility functions used in the fastai library"""

__version__ = "2.1.15"
