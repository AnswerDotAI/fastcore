# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/12_py2pyi.ipynb.

# %% auto 0
__all__ = ['functypes', 'imp_mod', 'has_deco', 'sig2str', 'ast_args', 'create_pyi', 'py2pyi']

# %% ../nbs/12_py2pyi.ipynb 3
import ast, sys, inspect, re, os, importlib.util, importlib.machinery

from ast import parse, unparse
from inspect import signature, getsource
from .utils import *
from .meta import delegates

# %% ../nbs/12_py2pyi.ipynb 5
def imp_mod(module_path, package=None):
    "Import dynamically the module referenced in `fn`"
    module_path = str(module_path)
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.machinery.ModuleSpec(module_name, None, origin=module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader = importlib.machinery.SourceFileLoader(module_name, module_path)
    if package is not None: module.__package__ = package
    module.__file__ = os.path.abspath(module_path)
    spec.loader.exec_module(module)
    return module

# %% ../nbs/12_py2pyi.ipynb 8
def _get_tree(mod):
    return parse(getsource(mod))

# %% ../nbs/12_py2pyi.ipynb 10
@patch
def __repr__(self:ast.AST):
    return unparse(self)

@patch
def _repr_markdown_(self:ast.AST):
    return f"""```python
{self!r}
```"""

# %% ../nbs/12_py2pyi.ipynb 13
functypes = (ast.FunctionDef,ast.AsyncFunctionDef)

# %% ../nbs/12_py2pyi.ipynb 15
def _deco_id(d:Union[ast.Name,ast.Attribute])->bool:
    "Get the id for AST node `d`"
    return d.id if isinstance(d, ast.Name) else d.func.id

def has_deco(node:Union[ast.FunctionDef,ast.AsyncFunctionDef], name:str)->bool:
    "Check if a function node `node` has a decorator named `name`"
    return any(_deco_id(d)==name for d in getattr(node, 'decorator_list', []))

# %% ../nbs/12_py2pyi.ipynb 21
def _get_proc(node):
    if isinstance(node, ast.ClassDef): return _proc_class
    if not isinstance(node, functypes): return None
    if not has_deco(node, 'delegates'): return _proc_body
    if has_deco(node, 'patch'): return _proc_patched
    return _proc_func

# %% ../nbs/12_py2pyi.ipynb 22
def _proc_tree(tree, mod):
    for node in tree.body:
        proc = _get_proc(node)
        if proc: proc(node, mod)

# %% ../nbs/12_py2pyi.ipynb 23
def _proc_mod(mod):
    tree = _get_tree(mod)
    _proc_tree(tree, mod)
    return tree

# %% ../nbs/12_py2pyi.ipynb 28
def sig2str(sig):
    s = str(sig)
    s = re.sub(r"<class '(.*?)'>", r'\1', s)
    s = re.sub(r"dynamic_module\.", "", s)
    return s

# %% ../nbs/12_py2pyi.ipynb 29
def ast_args(func):
    sig = signature(func)
    return ast.parse(f"def _{sig2str(sig)}: ...").body[0].args

# %% ../nbs/12_py2pyi.ipynb 33
def _body_ellip(n: ast.AST):
    stidx = 1 if isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Str) else 0
    n.body[stidx:] = [ast.Expr(ast.Constant(...))]

# %% ../nbs/12_py2pyi.ipynb 35
def _update_func(node, sym):
    """Replace the parameter list of the source code of a function `f` with a different signature.
    Replace the body of the function with just `pass`, and remove any decorators named 'delegates'"""
    node.args = ast_args(sym)
    _body_ellip(node)
    node.decorator_list = [d for d in node.decorator_list if _deco_id(d) != 'delegates']

# %% ../nbs/12_py2pyi.ipynb 38
def _proc_body(node, mod): _body_ellip(node)

# %% ../nbs/12_py2pyi.ipynb 39
def _proc_func(node, mod):
    sym = getattr(mod, node.name)
    _update_func(node, sym)

# %% ../nbs/12_py2pyi.ipynb 50
def _proc_patched(node, mod):
    ann = node.args.args[0].annotation
    if hasattr(ann, 'elts'): ann = ann.elts[0]
    cls = getattr(mod, ann.id)
    sym = getattr(cls, node.name)
    _update_func(node, sym)

# %% ../nbs/12_py2pyi.ipynb 55
def _proc_class(node, mod):
    cls = getattr(mod, node.name)
    _proc_tree(node, cls)

# %% ../nbs/12_py2pyi.ipynb 57
def create_pyi(fn, package=None):
    "Convert `fname.py` to `fname.pyi` by removing function bodies and expanding `delegates` kwargs"
    fn = Path(fn)
    mod = imp_mod(fn, package=package)
    tree = _proc_mod(mod)
    res = unparse(tree)
    fn.with_suffix('.pyi').write_text(res)

# %% ../nbs/12_py2pyi.ipynb 61
from .script import call_parse

# %% ../nbs/12_py2pyi.ipynb 62
@call_parse
def py2pyi(fname:str,  # The file name to convert
           package:str=None  # The parent package
          ):
    "Convert `fname.py` to `fname.pyi` by removing function bodies and expanding `delegates` kwargs"
    create_pyi(fname, package)
