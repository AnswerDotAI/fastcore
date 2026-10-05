"""Python supercharged for fastai development

Python is a powerful, dynamic language. Rather than bake everything into the language, it lets the programmer customize it to make it work for them. `fastcore` uses this flexibility to add to Python features inspired by other languages we've loved, mixins from Ruby, and currying, binding, and more from Haskell. It also adds some "missing features" and cleans up some rough edges in the Python standard library, such as simplifying parallel processing, and bringing ideas from NumPy over to Python's `list` type.

Here are some tips on using fastcore:

- Use `from fastcore.module import *` freely. fastcore's modules are built to be safe for wildcard imports.
- Use `L` in place of `list`. `L` behaves like a list, with extra indexing options, method chaining and more methods.
- Add methods to existing classes, including built-ins, with the `@patch` decorator instead of subclassing.
- In `__init__` methods, call `store_attr()` to set multiple attributes at once instead of assigning each one.
- Apply the `delegates` decorator to show a function's real parameters in place of `**kwargs`, for IDEs and generated documentation.
- Use fastcore's versions of `ThreadPoolExecutor` and `ProcessPoolExecutor` for simpler concurrent processing.
- Prefer fastcore's test functions, such as `test_eq`, `test_ne` and `test_close`, for assertions that read clearly and give informative failures.
- fastcore extends `pathlib.Path` with methods such as `ls()` and `read_json()`.
- Convert between dictionaries and objects with attribute access using `dict2obj` and `obj2dict`.
- Write in a functional style with tools such as `compose`, `maps` and `filter_ex`.
- Document parameters and return values with `docments`, using source comments or `Annotated` metadata for generated APIs. `MarkdownRenderer` shows the effective signature and keeps usage sections such as Notes, Raises and Examples.
- Apply the `timed_cache` decorator to add time-based expiry to the standard `lru_cache`.
- Turn Python functions into command-line interfaces with `fastcore.script`.

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

- `fastcore.aio`: Bridging async and sync code: `run_sync`, `iter_sync`, `ctx_sync`, `athreaded`, `maybe_await`, and `then`, plus `Debounce` for coalescing bursts of calls
- `fastcore.apisurface`: Signatures, documentation and grouped namespaces for generated API clients
- `fastcore.basics`: Basic functionality used in the fastai library
- `fastcore.docments`: Document parameters using comments.
- `fastcore.editskill`: Text, file, cell, and notebook editing from `fastcore.tools` and `fastcore.nbio`, plus the conventions the whole fastai editing toolkit follows. Read this before working with the editing tools in any package that shares them.
- `fastcore.foundation`: The `L` class and helpers for it
- `fastcore.meta`: Metaclasses
- `fastcore.nbio`: Reading, writing, and running Jupyter notebooks
- `fastcore.net`: Network, HTTP, and URL functions
- `fastcore.parallel`: Threading and multiprocessing functions
- `fastcore.script`: Creates a CLI from a Python function decorated with `call_parse`.
- `fastcore.style`: Fast styling for friendly CLIs.
- `fastcore.test`: Helper functions to quickly write tests in notebooks
- `fastcore.tools`: Text and file editing primitives shared by the fastai editing tools
- `fastcore.xdg`: XDG Base Directory Specification helpers.
- `fastcore.xml`: Concise HTML generation and namespace-aware XML construction.
- `fastcore.xtras`: Utility functions used in the fastai library"""

__version__ = "2.2.33"
