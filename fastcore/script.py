"""Creates a CLI from a Python function decorated with `call_parse`.

The function's parameters become the script's arguments, its docstring becomes the program description, and its [docments](https://fastcore.fast.ai/docments.html) comments become the help for each argument.

Here's a complete example (`examples/test_fastcore.py` in the fastcore repo):

```python
from fastcore.script import *
@call_parse
def main(
    msg:str, # The message
    upper:bool # Convert to uppercase?
):
    "Print `msg`, optionally converting to uppercase"
    print(msg.upper() if upper else msg)
```

Copy that into a file and run it, and you get a CLI with help, defaults, and error handling, with no `if __name__ == "__main__"` or argument parsing code:

```
$ examples/test_fastcore.py --help
usage: test_fastcore.py [-h] [--upper] msg

Print `msg`, optionally converting to uppercase

positional arguments:
  msg         The message

options:
  -h, --help  show this help message and exit
  --upper     Convert to uppercase? (default: False)
```

The function is still a plain Python function too, so it can also be called normally, e.g from a REPL such as Jupyter.

## Annotated params

For `argparse` features that docments can't express, use `typing.Annotated` type hints instead of plain types:

```python
from fastcore.script import *
from typing import Annotated
@call_parse
def main(msg:Annotated[str, "The message"],
         upper:Annotated[store_true, "Convert to uppercase?"]):
    "Print `msg`, optionally converting to uppercase"
    print(msg.upper() if upper else msg)
```

The first element of `Annotated` is the parameter's type, and the first string in its metadata is its help. A `dict` in the metadata passes extra arguments to argparse: its keys can be `opt`, `action`, `nargs`, `const`, `choices`, `required`, and `version`. All but `opt` go straight to `add_argument`; `opt` is a bool that overrides whether the param is a flag or positional, which is normally inferred from whether it has a default.

## Short flags

A capital letter in a parameter name declares a short flag: the capitalized letter becomes the short spelling and the lowercased name the long one, so `Resume:int=None` gets both `-r` and `--resume`. The capital can be any letter (`sUggest:str=None` gives `-u/--suggest`), only the first capital counts, and names without capitals get a long flag only. Since the flags are lowercased, the parameter's actual name keeps its capital -- so a Python caller writes `main(Resume=3)`, which usefully advertises that it's invoking a CLI entry point. Positional (default-less) parameters have no flags, so capitals there are left alone.

## Positional params

Parameters without a default are positional, and the rest are flags. Pass `pos` to `call_parse` (or to `anno_parser`) to keep named parameters positional even when they have a default, in which case they are optional on the command line and take the default when omitted. Command line order follows the signature, not the order of the names in `pos`. Naming a bool parameter in `pos` raises, since a flag takes no value.

## Param types

A `bool` parameter is a `store_true` flag defaulting to `False`. If its default is `True` it becomes a `--no-` prefixed `store_false` flag instead, so passing the flag turns it off. Use `bool_arg` as the type when you want an explicit `--flag true|false` argument that honors its default.

Union types such as `int|str` try each type in turn, and `enum` types such as those from `str_enum` become argparse choices.

## The CLI entry point

The decorated function is always the CLI entry point, and only the entry point gets `sys.argv`: argv is parsed when the function's file is run directly (`python foo.py`, `python -m foo`, or `%run foo.py`), or when it's called with no arguments from the top-level body of a directly-run file (which is how console script wrappers invoke it). Every other call is a plain Python call that ignores argv, whether from a notebook, the REPL, another function, or another `call_parse` function.

Use the `nested` keyword argument to create nested parsers, where earlier parsers consume only their known args from `sys.argv` before later parsers are used. This is useful to create one command line application that executes another. For example:

```sh
myrunner --keyword 1 script.py -- <script.py args>
```

A separating `--` after the first application's args is recommended though not always required, otherwise args may be parsed in unexpected ways. For example:

```sh
myrunner script.py -h
```

would display `myrunner`'s help and not `script.py`'s.

A function usable both from the command line and from Python can call `is_cli` to tell which way it was invoked, e.g. returning a value to Python callers but printing it (or exiting with an error code) when run as a CLI:

```python
@call_parse
def sum_args(a:int=0, b:int=0):
    "Add `a` and `b`"
    if is_cli(): print(a+b)
    else: return a+b

test_eq(sum_args(1,2), 3)  # Python call: returns the value, prints nothing
```

Docs: https://fastcore.fast.ai/script.html.md"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_script.ipynb.

# %% auto #0
__all__ = ['store_true', 'store_false', 'bool_arg', 'anno_parser', 'args_from_prog', 'set_ctx', 'call_parse', 'is_cli']

# %% ../nbs/06_script.ipynb #8a36db98
import inspect,argparse,shutil,types,asyncio,importlib.metadata

from functools import wraps,partial
from .imports import *
from .utils import *
from .docments import docments, ann_parts
from typing import get_origin, get_args, Union

# %% ../nbs/06_script.ipynb #5bf7ac6c
def store_true():
    "Placeholder annotation type for a `store_true` argparse action"
    pass

# %% ../nbs/06_script.ipynb #e2798370
def store_false():
    "Placeholder annotation type for a `store_false` argparse action"
    pass

# %% ../nbs/06_script.ipynb #69d525bc
def bool_arg(v):
    "Annotation type giving `bool` behavior for CLI args"
    return str2bool(v)

# %% ../nbs/06_script.ipynb #6785a783
def _arg_kw(k, anno, doc, default, extra):
    "CLI arg name and `add_argument` kwargs for param `k`"
    extra = dict(extra)
    action,d = extra.get('action'),extra.pop('default', default)
    opt,negated = extra.pop('opt', None),False
    if   anno==store_true:  action,d,anno = 'store_true',False,None
    elif anno==store_false: action,d,anno = 'store_false',True,None
    elif anno==bool and action is None:
        anno = None
        if d is True: action,negated = 'store_false',True
        else: action,d = 'store_true',False
    if action=='version':
        if 'version' not in extra and d is not inspect.Parameter.empty: extra['version'] = d
        return f'--{k}', {'help':doc or '', **extra}
    kw = {}
    if action and 'action' not in extra: kw['action'] = action
    if anno is not None:
        kw['type'] = anno
        if isinstance(anno,type) and issubclass(anno,enum.Enum): kw['choices'] = list(anno)
    if d is not inspect.Parameter.empty and d is not None: kw['default'] = d
    if opt is None: opt = d is not inspect.Parameter.empty
    kw['help'] = (doc or '') + (f" (default: {kw['default']})" if 'default' in kw else '')
    if negated: kw['dest'] = k
    name = f'no-{k}' if negated else k
    short = first(c for c in k if c.isupper()) if opt else None
    if short is None: return f"{'--' if opt else ''}{name}", {**kw, **extra}
    kw['dest'] = k  # flags are lowercased, so argparse's derived dest would drop the capital
    return (f'-{short.lower()}', f'--{name.lower()}'), {**kw, **extra}

# %% ../nbs/06_script.ipynb #cceb4486
class _HelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2):
        cols = shutil.get_terminal_size((120,30))[0]
        super().__init__(prog, max_help_position=cols//2, width=cols, indent_increment=indent_increment)
    def _expand_help(self, action): return self._get_help_string(action)

# %% ../nbs/06_script.ipynb #2259c093
def _is_union(t): return get_origin(t) in (Union, types.UnionType) if hasattr(types, 'UnionType') else get_origin(t) is Union

def _union_parser(types):
    "Return a parser that tries each type in sequence"
    def _parse(v):
        for t in types:
            if t is type(None): continue
            try: return t(v)
            except: pass
        raise ValueError(f"Could not parse {v!r} as any of {types}")
    return _parse

def _union_type(t):
    "Get parser for Union types, or None if not a Union"
    if not _is_union(t): return None
    return _union_parser(get_args(t))

# %% ../nbs/06_script.ipynb #347edc5a
def _pkg_version(func):
    "`name version` of the top-level package defining `func`, or None if it has no version"
    pkg = func.__module__.split('.')[0]
    if pkg=='__main__': return None
    ver = getattr(sys.modules.get(pkg), '__version__', None)
    if ver is None:
        try: ver = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError: return None
    return f'{pkg} {ver}'

# %% ../nbs/06_script.ipynb #5e5bea67
def anno_parser(func, prog:str=None, pos:list=None):
    "Look at params (with type/docments/`Annotated` annotations) in func and return an `ArgumentParser`"
    p = argparse.ArgumentParser(description=func.__doc__, prog=prog, formatter_class=_HelpFormatter, epilog=_pkg_version(func))
    for k,v in docments(func, full=True, returns=False, eval_str=True).items():
        anno,meta = ann_parts(v.anno)
        extra = next((o for o in meta if isinstance(o,dict)), {})
        if pos and k in pos:
            if anno in (bool,store_true,store_false): raise ValueError(f"positional param {k!r} can't be a bool: a flag takes no value")
            extra = merge({'opt':False}, {'nargs':'?'} if v.default is not inspect.Parameter.empty else {}, extra)
        anno = _union_type(anno) or anno
        name,kw = _arg_kw(k, anno, v.docment, v.default, extra)
        p.add_argument(*tuplify(name), **kw)
    p.add_argument(f"--pdb", help=argparse.SUPPRESS, action='store_true')
    p.add_argument(f"--xtra", help=argparse.SUPPRESS, type=str)
    return p

# %% ../nbs/06_script.ipynb #75e8a419
def args_from_prog(func, prog):
    "Extract args from `prog`"
    if prog is None or '#' not in prog: return {}
    if '##' in prog: _,prog = prog.split('##', 1)
    progsp = prog.split("#")
    args = {progsp[i]:progsp[i+1] for i in range(0, len(progsp), 2)}
    annos = type_hints(func)
    for k,v in args.items():
        t,meta = ann_parts(annos.get(k))
        extra = next((o for o in meta if isinstance(o,dict)), {})
        if t in (bool, bool_arg, store_true, store_false) or extra.get('action') in ('store_true','store_false'): t = str2bool
        if t: args[k] = t(v)
    return args

# %% ../nbs/06_script.ipynb #42c8e85f
from contextvars import ContextVar
from contextlib import contextmanager

# %% ../nbs/06_script.ipynb #e4537112
@contextmanager
def set_ctx(cv, val=True):
    token = cv.set(val)
    try: yield
    finally: cv.reset(token)

# %% ../nbs/06_script.ipynb #fc816498
def _is_script_run(frame):
    "True if `frame` is the top-level body of a file being run directly (`python foo.py`, `python -m foo`, or `%run foo.py`)"
    if not frame or frame.f_locals is not frame.f_globals: return False
    g = frame.f_globals
    if g.get('__name__')!='__main__' or not g.get('__file__'): return False
    return Path(g['__file__']).resolve()==Path(frame.f_code.co_filename).resolve()

# %% ../nbs/06_script.ipynb #dee5e259
_cli_func = ContextVar('_cli_func', default=None)

def _run_cli(func, nested, pos=None):
    "Parse `sys.argv` with `anno_parser` and call `func` with the result"
    with set_ctx(_cli_func, func):
        if len(sys.argv)>1 and sys.argv[1]=='': sys.argv.pop(1)
        p = anno_parser(func, pos=pos)
        if nested: args, sys.argv[1:] = p.parse_known_args()
        else: args = p.parse_args()
        args = args.__dict__
        xtra = otherwise(args.pop('xtra', ''), eq(1), p.prog)
        tfunc = trace(func) if args.pop('pdb', False) else func
        res = tfunc(**merge(args, args_from_prog(func, xtra)))
        return asyncio.run(res) if inspect.isawaitable(res) else res

def call_parse(func=None, nested=False, pos:list=None):
    "Decorator to create a simple CLI from `func` using `anno_parser`"
    if func is None: return partial(call_parse, nested=nested, pos=pos)
    @wraps(func)
    def _f(*args, **kwargs):
        if args or kwargs or _cli_func.get() is not None: return func(*args, **kwargs)
        if _is_script_run(inspect.currentframe().f_back): return _run_cli(func, nested, pos)
        with set_ctx(_cli_func, False): return func(*args, **kwargs)

    frame = inspect.currentframe().f_back
    if _is_script_run(frame):
        frame.f_globals[func.__name__] = _f
        return _run_cli(func, nested, pos)
    else: return _f

# %% ../nbs/06_script.ipynb #f4961093
def is_cli(func=None):
    "True if a `call_parse` CLI run is in progress, optionally checking that `func` is the function being run"
    f = _cli_func.get()
    return bool(f) if func is None else f is getattr(func, '__wrapped__', func)
