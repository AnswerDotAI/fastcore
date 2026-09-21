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

`call_parse` provides argument parsing, help, defaults and error handling. Copy the example into a file and run it without adding an `if __name__ == "__main__"` block:

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

You can also call the function normally from Python, including in a Jupyter notebook.

## Annotated params

Use `typing.Annotated` for `argparse` options that docments can't express:

```python
from fastcore.script import *
from typing import Annotated
@call_parse
def main(msg:Annotated[str, "The message"],
         upper:Annotated[store_true, "Convert to uppercase?"]):
    "Print `msg`, optionally converting to uppercase"
    print(msg.upper() if upper else msg)
```

The first element is the parameter's type. The first string in its metadata provides help text. Add a metadata dictionary to set `action`, `nargs`, `const`, `choices`, `required` or `version` arguments for `argparse.add_argument`.

The dictionary also accepts `opt`. Set it to `True` for a flag or `False` for a positional parameter. Without `opt`, parameters with defaults become flags.

## Short flags

The first capital letter in an optional parameter's name declares a short flag:

- `Resume:int=None` gives `-r` and `--resume`.
- `sUggest:str=None` gives `-u` and `--suggest`.
- Names without capitals have only a long flag.

Long flags use lowercase and hyphens, such as `--cache-dir` for `cache_dir`. Python calls keep the parameter's spelling, such as `main(Resume=3)`. Positional parameters have no flags and keep their names unchanged.

## Positional params

Parameters without defaults are positional. Other parameters become flags. `*args` accepts zero or more positional values. Parameters after it are flags. CLI calls ignore `**kwargs`.

Pass parameter names in `pos` to `call_parse` or `anno_parser` to keep them positional even with defaults. Omitted values use those defaults. Command-line order follows the signature, regardless of the order in `pos`. A boolean flag cannot appear in `pos` because it takes no value.

## Param types

A `bool` parameter is a `store_true` flag defaulting to `False`. If its default is `True` it becomes a `--no-` prefixed `store_false` flag instead, so passing the flag turns it off. Use `bool_arg` as the type when you want an explicit `--flag true|false` argument that honors its default.

`argparse` normally repeats an option's name as its value placeholder, such as `--path PATH`. Here help shows the type instead, such as `--path (str)`.

`anno2str` formats the type name. It displays `Path` as `path`. Unions list each type once and omit `str` when `path` is present. For example, `Path|str` displays as `path`.

Enums show their choices as `{choice,...}`. Positional parameters show their names.

Union types such as `int|str` try each type in turn, and `enum` types such as those from `str_enum` become argparse choices.

`parse_cli` is the argument-handling half of a `call_parse` run. It parses `sys.argv` for `func`. It returns the positional arguments, the keyword arguments, and whether `--pdb` was passed. `call_parse` then calls `func` with them. Use `parse_cli` to write a decorator that reads arguments as `call_parse` does and runs `func` some other way. [warmpy](https://github.com/AnswerDotAI/warmpy) runs it in a warm background process.

## The CLI entry point

`call_parse` parses `sys.argv` when you run the function's file directly with `python foo.py`, `python -m foo` or `%run foo.py`. It also parses arguments on a zero-argument call from the top-level body of a directly run file. Console-script wrappers use this form.

Calls from a notebook, REPL or another function are ordinary Python calls. This includes calls from another `call_parse` function.

CLI calls return integers, including booleans, as exit codes. They discard other return values. Python calls preserve return values. Raise `CliError` to report an error message to CLI users.

Set `nested=True` when one CLI launches another. The outer parser removes the arguments it recognizes from `sys.argv`, leaving the rest for the inner CLI:

```sh
myrunner --keyword 1 script.py -- <script.py args>
```

`--` is optional in some invocations. Use it to separate the applications' arguments and avoid cases such as:

```sh
myrunner script.py -h
```

`myrunner` handles `-h` here instead of passing it to `script.py`.

Use `is_cli` to distinguish CLI execution from Python calls. Here the CLI prints a result that Python callers receive as a return value:

```python
@call_parse
def sum_args(a:int=0, b:int=0):
    "Add `a` and `b`"
    if is_cli(): print(a+b)
    else: return a+b

test_eq(sum_args(1,2), 3)  # Python call: returns the value, prints nothing
```

Raise `CliError` when a command cannot continue. CLI execution prints its message to stderr and exits with status 1. Python callers can catch the exception:

```python
@call_parse
def show(fname:str=None):
    "Print `fname`"
    if fname is None: raise CliError("fname is required")
    print(fname)

with expect_fail(CliError, contains='fname is required'): show()
```

Docs: https://fastcore.fast.ai/script.html.md"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_script.ipynb.

# %% auto #0
__all__ = ['store_true', 'store_false', 'bool_arg', 'anno2str', 'anno_parser', 'args_from_prog', 'set_ctx', 'parse_cli',
           'call_parse', 'is_cli', 'CliError']

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
def _arg_kw(k, anno, doc, default, extra, mv=None):
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
        return f'--{k.replace("_", "-")}', {'help':doc or '', **extra}
    kw = {}
    if action and 'action' not in extra: kw['action'] = action
    if anno is not None:
        kw['type'] = anno
        if isinstance(anno,type) and issubclass(anno,enum.Enum): kw['choices'] = list(anno)
    if d is not inspect.Parameter.empty and d is not None: kw['default'] = d
    if opt is None: opt = d is not inspect.Parameter.empty
    if mv and opt and 'type' in kw and 'choices' not in kw and 'choices' not in extra: kw['metavar'] = f'({mv})'
    dshow = repr(d) if isinstance(d,str) and not d.strip() else d
    kw['help'] = (doc or '') + (f" (default: {dshow})" if 'default' in kw else '')
    if negated: kw['dest'] = k
    name = f'no-{k}' if negated else k
    if opt: name = name.replace('_', '-')
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

# %% ../nbs/06_script.ipynb #e7d31e68
def anno2str(t):
    "Display name for CLI annotation `t`, e.g. for an argparse metavar"
    if t is None: return None
    if _is_union(t):
        nms = dict.fromkeys(anno2str(o) for o in get_args(t) if o is not type(None))
        if 'path' in nms: nms.pop('str', None)
        return '|'.join(nms)
    if isinstance(t,type) and issubclass(t,Path): return 'path'
    if t is bool_arg: return 'bool'
    return getattr(t, '__name__', str(t))

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
        if v.kind is inspect.Parameter.VAR_KEYWORD: continue
        anno,meta = ann_parts(v.anno)
        extra = next((o for o in meta if isinstance(o,dict)), {})
        if v.kind is inspect.Parameter.VAR_POSITIONAL:
            if anno in (bool,store_true,store_false): raise ValueError(f"variadic param {k!r} can't be a bool: a flag takes no value")
            extra = merge({'opt':False, 'nargs':'*'}, extra)
        elif pos and k in pos:
            if anno in (bool,store_true,store_false): raise ValueError(f"positional param {k!r} can't be a bool: a flag takes no value")
            extra = merge({'opt':False}, {'nargs':'?'} if v.default is not inspect.Parameter.empty else {}, extra)
        mv = anno2str(anno)
        anno = _union_type(anno) or anno
        name,kw = _arg_kw(k, anno, v.docment, v.default, extra, mv)
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

# %% ../nbs/06_script.ipynb #d9a3f93c
def _pos_split(func, args):
    "Pop values for params up to a `*args` param from `args` in signature order, to pass positionally"
    ks = []
    for k,v in inspect.signature(func).parameters.items():
        if v.kind is inspect.Parameter.VAR_POSITIONAL: return [args.pop(o) for o in ks]+list(args.pop(k)), args
        ks.append(k)
    return [],args

# %% ../nbs/06_script.ipynb #1456b39c
def parse_cli(func, nested=False, pos:list=None):
    "Positional args, keyword args, and the `--pdb` flag that `sys.argv` gives for `func`"
    if len(sys.argv)>1 and sys.argv[1]=='': sys.argv.pop(1)
    p = anno_parser(func, pos=pos)
    if nested: args, sys.argv[1:] = p.parse_known_args()
    else: args = p.parse_args()
    args = args.__dict__
    xtra = otherwise(args.pop('xtra', ''), eq(1), p.prog)
    pdb = args.pop('pdb', False)
    return *_pos_split(func, merge(args, args_from_prog(func, xtra))), pdb

# %% ../nbs/06_script.ipynb #dee5e259
_cli_func = ContextVar('_cli_func', default=None)

def _run_cli(func, nested, pos=None):
    "Call `func` with the arguments `parse_cli` reads from `sys.argv`"
    with set_ctx(_cli_func, func):
        pargs,args,pdb = parse_cli(func, nested, pos)
        tfunc = trace(func) if pdb else func
        try:
            res = tfunc(*pargs, **args)
            if inspect.isawaitable(res): res = asyncio.run(res)
            return res if isinstance(res, int) else None
        except CliError as e: raise SystemExit(str(e))

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

# %% ../nbs/06_script.ipynb #46ea4457
class CliError(Exception):
    "Raised when a command can't continue: a CLI run exits with the message, a Python call sees the exception"
