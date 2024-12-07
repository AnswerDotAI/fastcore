"""The `L` class and helpers for it"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_foundation.ipynb.

# %% auto 0
__all__ = ['working_directory', 'add_docs', 'docs', 'coll_repr', 'is_bool', 'mask2idxs', 'cycle', 'zip_cycle', 'is_indexer',
           'CollBase', 'L', 'save_config_file', 'read_config_file', 'Config']

# %% ../nbs/02_foundation.ipynb
from .imports import *
from .basics import *
from functools import lru_cache
from contextlib import contextmanager
from copy import copy
from configparser import ConfigParser
import random,pickle,inspect

# %% ../nbs/02_foundation.ipynb
@contextmanager
def working_directory(path):
    "Change working directory to `path` and return to previous on exit."
    prev_cwd = Path.cwd()
    os.chdir(path)
    try: yield
    finally: os.chdir(prev_cwd)

# %% ../nbs/02_foundation.ipynb
def add_docs(cls, cls_doc=None, **docs):
    "Copy values from `docs` to `cls` docstrings, and confirm all public methods are documented"
    if cls_doc is not None: cls.__doc__ = cls_doc
    for k,v in docs.items():
        f = getattr(cls,k)
        if hasattr(f,'__func__'): f = f.__func__ # required for class methods
        f.__doc__ = v
    # List of public callables without docstring
    nodoc = [c for n,c in vars(cls).items() if callable(c)
             and not n.startswith('_') and c.__doc__ is None]
    assert not nodoc, f"Missing docs: {nodoc}"
    assert cls.__doc__ is not None, f"Missing class docs: {cls}"

# %% ../nbs/02_foundation.ipynb
def docs(cls):
    "Decorator version of `add_docs`, using `_docs` dict"
    add_docs(cls, **cls._docs)
    return cls

# %% ../nbs/02_foundation.ipynb
def coll_repr(c, max_n=20):
    "String repr of up to `max_n` items of (possibly lazy) collection `c`"
    return f'(#{len(c)}) [' + ','.join(itertools.islice(map(repr,c), max_n)) + (
        '...' if len(c)>max_n else '') + ']'

# %% ../nbs/02_foundation.ipynb
def is_bool(x):
    "Check whether `x` is a bool or None"
    return isinstance(x,(bool,NoneType)) or risinstance('bool_', x)

# %% ../nbs/02_foundation.ipynb
def mask2idxs(mask):
    "Convert bool mask or index list to index `L`"
    if isinstance(mask,slice): return mask
    mask = list(mask)
    if len(mask)==0: return []
    it = mask[0]
    if hasattr(it,'item'): it = it.item()
    if is_bool(it): return [i for i,m in enumerate(mask) if m]
    return [int(i) for i in mask]

# %% ../nbs/02_foundation.ipynb
def cycle(o):
    "Like `itertools.cycle` except creates list of `None`s if `o` is empty"
    o = listify(o)
    return itertools.cycle(o) if o is not None and len(o) > 0 else itertools.cycle([None])

# %% ../nbs/02_foundation.ipynb
def zip_cycle(x, *args):
    "Like `itertools.zip_longest` but `cycle`s through elements of all but first argument"
    return zip(x, *map(cycle,args))

# %% ../nbs/02_foundation.ipynb
def is_indexer(idx):
    "Test whether `idx` will index a single item in a list"
    return isinstance(idx,int) or not getattr(idx,'ndim',1)

# %% ../nbs/02_foundation.ipynb
class CollBase:
    "Base class for composing a list of `items`"
    def __init__(self, items): self.items = items
    def __len__(self): return len(self.items)
    def __getitem__(self, k): return self.items[list(k) if isinstance(k,CollBase) else k]
    def __setitem__(self, k, v): self.items[list(k) if isinstance(k,CollBase) else k] = v
    def __delitem__(self, i): del(self.items[i])
    def __repr__(self): return self.items.__repr__()
    def __iter__(self): return self.items.__iter__()

# %% ../nbs/02_foundation.ipynb
class _L_Meta(type):
    def __call__(cls, x=None, *args, **kwargs):
        if not args and not kwargs and x is not None and isinstance(x,cls): return x
        return super().__call__(x, *args, **kwargs)

# %% ../nbs/02_foundation.ipynb
class L(GetAttr, CollBase, metaclass=_L_Meta):
    "Behaves like a list of `items` but can also index with list of indices or masks"
    _default='items'
    def __init__(self, items=None, *rest, use_list=False, match=None):
        if (use_list is not None) or not is_array(items):
            items = listify(items, *rest, use_list=use_list, match=match)
        super().__init__(items)

    @property
    def _xtra(self): return None
    def _new(self, items, *args, **kwargs): return type(self)(items, *args, use_list=None, **kwargs)
    def __getitem__(self, idx):
        if isinstance(idx,int): return self.items[idx]
        return self._get(idx) if is_indexer(idx) else L(self._get(idx), use_list=None)
    def copy(self): return self._new(self.items.copy())

    def _get(self, i):
        if is_indexer(i) or isinstance(i,slice): return getattr(self.items,'iloc',self.items)[i]
        i = mask2idxs(i)
        return (self.items.iloc[list(i)] if hasattr(self.items,'iloc')
                else self.items.__array__()[(i,)] if hasattr(self.items,'__array__')
                else [self.items[i_] for i_ in i])

    def __setitem__(self, idx, o):
        "Set `idx` (can be list of indices, or mask, or int) items to `o` (which is broadcast if not iterable)"
        if isinstance(idx, int): self.items[idx] = o
        else:
            idx = idx if isinstance(idx,L) else listify(idx)
            if not is_iter(o): o = [o]*len(idx)
            for i,o_ in zip(idx,o): self.items[i] = o_

    def __eq__(self,b):
        if b is None: return False
        if not hasattr(b, '__iter__'): return False
        if risinstance('ndarray', b): return array_equal(b, self)
        if isinstance(b, (str,dict)) or callable(b): return False
        return all_equal(b,self)

    def sorted(self, key=None, reverse=False, cmp=None, **kwargs): return self._new(sorted_ex(self, key=key, reverse=reverse, cmp=cmp, **kwargs))
    def __iter__(self): return iter(self.items.itertuples() if hasattr(self.items,'iloc') else self.items)
    def __contains__(self,b): return b in self.items
    def __reversed__(self): return self._new(reversed(self.items))
    def __invert__(self): return self._new(not i for i in self)
    def __repr__(self): return repr(self.items)
    def _repr_pretty_(self, p, cycle):
        p.text('...' if cycle else repr(self.items) if is_array(self.items) else coll_repr(self))
    def __mul__ (a,b): return a._new(a.items*b)
    def __add__ (a,b): return a._new(a.items+listify(b))
    def __radd__(a,b): return a._new(b)+a
    def __addi__(a,b):
        a.items += list(b)
        return a

    @classmethod
    def split(cls, s, sep=None, maxsplit=-1): return cls(s.split(sep,maxsplit))
    @classmethod
    def splitlines(cls, s, keepends=False): return cls(s.splitslines(keepends))
    @classmethod
    def range(cls, a, b=None, step=None): return cls(range_of(a, b=b, step=step))

    def map(self, f, *args, **kwargs): return self._new(map_ex(self, f, *args, gen=False, **kwargs))
    def argwhere(self, f, negate=False, **kwargs): return self._new(argwhere(self, f, negate, **kwargs))
    def argfirst(self, f, negate=False): 
        if negate: f = not_(f)
        return first(i for i,o in self.enumerate() if f(o))
    def filter(self, f=noop, negate=False, **kwargs):
        return self._new(filter_ex(self, f=f, negate=negate, gen=False, **kwargs))

    def enumerate(self): return L(enumerate(self))
    def renumerate(self): return L(renumerate(self))
    def unique(self, sort=False, bidir=False, start=None): return L(uniqueify(self, sort=sort, bidir=bidir, start=start))
    def val2idx(self): return val2idx(self)
    def cycle(self): return cycle(self)
    def groupby(self, key, val=noop): return L(groupby(self, key, val=val))
    def map_dict(self, f=noop, *args, **kwargs): return {k:f(k, *args,**kwargs) for k in self}
    def map_first(self, f=noop, g=noop, *args, **kwargs):
        return first(self.map(f, *args, **kwargs), g)

    def itemgot(self, *idxs):
        x = self
        for idx in idxs: x = x.map(itemgetter(idx))
        return x
    def attrgot(self, k, default=None):
        return self.map(lambda o: o.get(k,default) if isinstance(o, dict) else nested_attr(o,k,default))

    def starmap(self, f, *args, **kwargs): return self._new(itertools.starmap(partial(f,*args,**kwargs), self))
    def zip(self, cycled=False): return self._new((zip_cycle if cycled else zip)(*self))
    def zipwith(self, *rest, cycled=False): return self._new([self, *rest]).zip(cycled=cycled)
    def map_zip(self, f, *args, cycled=False, **kwargs): return self.zip(cycled=cycled).starmap(f, *args, **kwargs)
    def map_zipwith(self, f, *rest, cycled=False, **kwargs): return self.zipwith(*rest, cycled=cycled).starmap(f, **kwargs)
    def shuffle(self):
        it = copy(self.items)
        random.shuffle(it)
        return self._new(it)

    def concat(self): return self._new(itertools.chain.from_iterable(self.map(L)))
    def reduce(self, f, initial=None): return reduce(f, self) if initial is None else reduce(f, self, initial)
    def sum(self): return self.reduce(operator.add, 0)
    def product(self): return self.reduce(operator.mul, 1)
    def setattrs(self, attr, val): [setattr(o,attr,val) for o in self]

# %% ../nbs/02_foundation.ipynb
add_docs(L,
         __getitem__="Retrieve `idx` (can be list of indices, or mask, or int) items",
         range="Class Method: Same as `range`, but returns `L`. Can pass collection for `a`, to use `len(a)`",
         split="Class Method: Same as `str.split`, but returns an `L`",
         splitlines="Class Method: Same as `str.splitlines`, but returns an `L`",
         copy="Same as `list.copy`, but returns an `L`",
         sorted="New `L` sorted by `key`, using `sort_ex`. If key is str use `attrgetter`; if int use `itemgetter`",
         unique="Unique items, in stable order",
         val2idx="Dict from value to index",
         filter="Create new `L` filtered by predicate `f`, passing `args` and `kwargs` to `f`",
         argwhere="Like `filter`, but return indices for matching items",
         argfirst="Return index of first matching item",
         map="Create new `L` with `f` applied to all `items`, passing `args` and `kwargs` to `f`",
         map_first="First element of `map_filter`",
         map_dict="Like `map`, but creates a dict from `items` to function results",
         starmap="Like `map`, but use `itertools.starmap`",
         itemgot="Create new `L` with item `idx` of all `items`",
         attrgot="Create new `L` with attr `k` (or value `k` for dicts) of all `items`.",
         cycle="Same as `itertools.cycle`",
         enumerate="Same as `enumerate`",
         renumerate="Same as `renumerate`",
         groupby="Same as `groupby`",
         zip="Create new `L` with `zip(*items)`",
         zipwith="Create new `L` with `self` zip with each of `*rest`",
         map_zip="Combine `zip` and `starmap`",
         map_zipwith="Combine `zipwith` and `starmap`",
         concat="Concatenate all elements of list",
         shuffle="Same as `random.shuffle`, but not inplace",
         reduce="Wrapper for `functools.reduce`",
         sum="Sum of the items",
         product="Product of the items",
         setattrs="Call `setattr` on all items")

# %% ../nbs/02_foundation.ipynb
# Here we are fixing the signature of L. What happens is that the __call__ method on the MetaClass of L shadows the __init__
# giving the wrong signature (https://stackoverflow.com/questions/49740290/call-from-metaclass-shadows-signature-of-init).
def _f(items=None, *rest, use_list=False, match=None): ...
L.__signature__ = inspect.signature(_f)

# %% ../nbs/02_foundation.ipynb
Sequence.register(L);

# %% ../nbs/02_foundation.ipynb
def save_config_file(file, d, **kwargs):
    "Write settings dict to a new config file, or overwrite the existing one."
    config = ConfigParser(**kwargs)
    config['DEFAULT'] = d
    config.write(open(file, 'w'))

# %% ../nbs/02_foundation.ipynb
def read_config_file(file, **kwargs):
    config = ConfigParser(**kwargs)
    config.read(file, encoding='utf8')
    return config['DEFAULT']

# %% ../nbs/02_foundation.ipynb
class Config:
    "Reading and writing `ConfigParser` ini files"
    def __init__(self, cfg_path, cfg_name, create=None, save=True, extra_files=None, types=None):
        self.types = types or {}
        cfg_path = Path(cfg_path).expanduser().absolute()
        self.config_path,self.config_file = cfg_path,cfg_path/cfg_name
        self._cfg = ConfigParser()
        self.d = self._cfg['DEFAULT']
        found = [Path(o) for o in self._cfg.read(L(extra_files)+[self.config_file], encoding='utf8')]
        if self.config_file not in found and create is not None:
            self._cfg.read_dict({'DEFAULT':create})
            if save:
                cfg_path.mkdir(exist_ok=True, parents=True)
                save_config_file(self.config_file, create)

    def __repr__(self): return repr(dict(self._cfg.items('DEFAULT', raw=True)))
    def __setitem__(self,k,v): self.d[k] = str(v)
    def __contains__(self,k):  return k in self.d
    def save(self):            save_config_file(self.config_file,self.d)
    def __getattr__(self,k):   return stop(AttributeError(k)) if k=='d' or k not in self.d else self.get(k)
    def __getitem__(self,k):   return stop(IndexError(k)) if k not in self.d else self.get(k)

    def get(self,k,default=None):
        v = self.d.get(k, default)
        if v is None: return None
        typ = self.types.get(k, None)
        if typ==bool: return str2bool(v)
        if not typ: return str(v)
        if typ==Path: return self.config_path/v
        return typ(v)

    def path(self,k,default=None):
        v = self.get(k, default)
        return v if v is None else self.config_path/v

    @classmethod
    def find(cls, cfg_name, cfg_path=None, **kwargs):
        "Search `cfg_path` and its parents to find `cfg_name`"
        p = Path(cfg_path or Path.cwd()).expanduser().absolute()
        return first(cls(o, cfg_name, **kwargs)
                      for o in [p, *p.parents] if (o/cfg_name).exists())
