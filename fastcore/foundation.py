# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_foundation.ipynb (unless otherwise specified).

__all__ = ['copy_func', 'patch_to', 'patch', 'patch_property', 'working_directory', 'add_docs', 'docs', 'coll_repr',
           'is_bool', 'mask2idxs', 'cycle', 'zip_cycle', 'is_indexer', 'GetAttr', 'delegate_attr', 'CollBase', 'L',
           'save_config_file', 'read_config_file', 'Config']

# Cell
from .imports import *
from .basics import *
from functools import lru_cache
from contextlib import contextmanager
from copy import copy
from configparser import ConfigParser
import random,pickle

# Cell
def copy_func(f):
    "Copy a non-builtin function (NB `copy.copy` does not work for this)"
    if not isinstance(f,FunctionType): return copy(f)
    fn = FunctionType(f.__code__, f.__globals__, f.__name__, f.__defaults__, f.__closure__)
    fn.__kwdefaults__ = f.__kwdefaults__
    fn.__dict__.update(f.__dict__)
    return fn

# Cell
def patch_to(cls, as_prop=False, cls_method=False):
    "Decorator: add `f` to `cls`"
    if not isinstance(cls, (tuple,list)): cls=(cls,)
    def _inner(f):
        for c_ in cls:
            nf = copy_func(f)
            # `functools.update_wrapper` when passing patched function to `Pipeline`, so we do it manually
            for o in functools.WRAPPER_ASSIGNMENTS: setattr(nf, o, getattr(f,o))
            nf.__qualname__ = f"{c_.__name__}.{f.__name__}"
            if cls_method:
                setattr(c_, f.__name__, MethodType(nf, c_))
            else:
                setattr(c_, f.__name__, property(nf) if as_prop else nf)
        return f
    return _inner

# Cell
def patch(f=None, *, as_prop=False, cls_method=False):
    "Decorator: add `f` to the first parameter's class (based on f's type annotations)"
    if f is None: return partial(patch, as_prop=as_prop, cls_method=cls_method)
    cls = next(iter(f.__annotations__.values()))
    return patch_to(cls, as_prop=as_prop, cls_method=cls_method)(f)

# Cell
def patch_property(f):
    "Deprecated; use `patch(as_prop=True)` instead"
    warnings.warn("`patch_property` is deprecated and will be removed; use `patch(as_prop=True)` instead")
    cls = next(iter(f.__annotations__.values()))
    return patch_to(cls, as_prop=True)(f)

# Cell
@contextmanager
def working_directory(path):
    "Change working directory to `path` and return to previous on exit."
    prev_cwd = Path.cwd()
    os.chdir(path)
    try: yield
    finally: os.chdir(prev_cwd)

# Cell
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

# Cell
def docs(cls):
    "Decorator version of `add_docs`, using `_docs` dict"
    add_docs(cls, **cls._docs)
    return cls

# Cell
def coll_repr(c, max_n=10):
    "String repr of up to `max_n` items of (possibly lazy) collection `c`"
    return f'(#{len(c)}) [' + ','.join(itertools.islice(map(repr,c), max_n)) + (
        '...' if len(c)>max_n else '') + ']'

# Cell
def is_bool(x):
    "Check whether `x` is a bool or None"
    return isinstance(x,(bool,NoneType)) or isinstance(x, 'bool_')

# Cell
def mask2idxs(mask):
    "Convert bool mask or index list to index `L`"
    if isinstance(mask,slice): return mask
    mask = list(mask)
    if len(mask)==0: return []
    it = mask[0]
    if hasattr(it,'item'): it = it.item()
    if is_bool(it): return [i for i,m in enumerate(mask) if m]
    return [int(i) for i in mask]

# Cell
def cycle(o):
    "Like `itertools.cycle` except creates list of `None`s if `o` is empty"
    o = listify(o)
    return itertools.cycle(o) if o is not None and len(o) > 0 else itertools.cycle([None])

# Cell
def zip_cycle(x, *args):
    "Like `itertools.zip_longest` but `cycle`s through elements of all but first argument"
    return zip(x, *map(cycle,args))

# Cell
def is_indexer(idx):
    "Test whether `idx` will index a single item in a list"
    return isinstance(idx,int) or not getattr(idx,'ndim',1)

# Cell
class GetAttr:
    "Inherit from this to have all attr accesses in `self._xtra` passed down to `self.default`"
    _default='default'
    def _component_attr_filter(self,k):
        if k.startswith('__') or k in ('_xtra',self._default): return False
        xtra = getattr(self,'_xtra',None)
        return xtra is None or k in xtra
    def _dir(self): return [k for k in dir(getattr(self,self._default)) if self._component_attr_filter(k)]
    def __getattr__(self,k):
        if self._component_attr_filter(k):
            attr = getattr(self,self._default,None)
            if attr is not None: return getattr(attr,k)
        raise AttributeError(k)
    def __dir__(self): return custom_dir(self,self._dir())
#     def __getstate__(self): return self.__dict__
    def __setstate__(self,data): self.__dict__.update(data)

# Cell
def delegate_attr(self, k, to):
    "Use in `__getattr__` to delegate to attr `to` without inheriting from `GetAttr`"
    if k.startswith('_') or k==to: raise AttributeError(k)
    try: return getattr(getattr(self,to), k)
    except AttributeError: raise AttributeError(k) from None

# Cell
class CollBase:
    "Base class for composing a list of `items`"
    def __init__(self, items): self.items = items
    def __len__(self): return len(self.items)
    def __getitem__(self, k): return self.items[list(k) if isinstance(k,CollBase) else k]
    def __setitem__(self, k, v): self.items[list(k) if isinstance(k,CollBase) else k] = v
    def __delitem__(self, i): del(self.items[i])
    def __repr__(self): return self.items.__repr__()
    def __iter__(self): return self.items.__iter__()

# Cell
class _L_Meta(type):
    def __call__(cls, x=None, *args, **kwargs):
        if not args and not kwargs and x is not None and isinstance(x,cls): return x
        return super().__call__(x, *args, **kwargs)

# Cell
class L(GetAttr, CollBase, metaclass=_L_Meta):
    "Behaves like a list of `items` but can also index with list of indices or masks"
    _default='items'
    def __init__(self, items=None, *rest, use_list=False, match=None):
        if rest: items = (items,)+rest
        if items is None: items = []
        if (use_list is not None) or not is_array(items):
            items = list(items) if use_list else listify(items)
        if match is not None:
            if is_coll(match): match = len(match)
            if len(items)==1: items = items*match
            else: assert len(items)==match, 'Match length mismatch'
        super().__init__(items)

    @property
    def _xtra(self): return None
    def _new(self, items, *args, **kwargs): return type(self)(items, *args, use_list=None, **kwargs)
    def __getitem__(self, idx): return self._get(idx) if is_indexer(idx) else L(self._get(idx), use_list=None)
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
        if isinstance(b, 'ndarray'): return array_equal(b, self)
        if isinstance(b, (str,dict)): return False
        return all_equal(b,self)

    def sorted(self, key=None, reverse=False): return self._new(sorted_ex(self, key=key, reverse=reverse))
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
    def range(cls, a, b=None, step=None): return cls(range_of(a, b=b, step=step))

    def map(self, f, *args, gen=False, **kwargs): return self._new(map_ex(self, f, *args, gen=gen, **kwargs))
    def argwhere(self, f, negate=False, **kwargs): return self._new(argwhere(self, f, negate, **kwargs))
    def filter(self, f=noop, negate=False, gen=False, **kwargs):
        return self._new(filter_ex(self, f=f, negate=negate, gen=gen, **kwargs))

    def unique(self): return L(dict.fromkeys(self).keys())
    def enumerate(self): return L(enumerate(self))
    def renumerate(self): return L(renumerate(self))
    def val2idx(self): return {v:k for k,v in self.enumerate()}
    def itemgot(self, *idxs):
        x = self
        for idx in idxs: x = x.map(itemgetter(idx))
        return x

    def attrgot(self, k, default=None):
        return self.map(lambda o: o.get(k,default) if isinstance(o, dict) else nested_attr(o,k,default))
    def cycle(self): return cycle(self)
    def map_dict(self, f=noop, *args, gen=False, **kwargs): return {k:f(k, *args,**kwargs) for k in self}
    def map_first(self, f=noop, g=noop, *args, **kwargs):
        return first(self.map(f, *args, gen=False, **kwargs), g)

    def starmap(self, f, *args, **kwargs): return self._new(itertools.starmap(partial(f,*args,**kwargs), self))
    def zip(self, cycled=False): return self._new((zip_cycle if cycled else zip)(*self))
    def zipwith(self, *rest, cycled=False): return self._new([self, *rest]).zip(cycled=cycled)
    def map_zip(self, f, *args, cycled=False, **kwargs): return self.zip(cycled=cycled).starmap(f, *args, **kwargs)
    def map_zipwith(self, f, *rest, cycled=False, **kwargs):
        return self.zipwith(*rest, cycled=cycled).starmap(f, **kwargs)
    def shuffle(self):
        it = copy(self.items)
        random.shuffle(it)
        return self._new(it)

    def concat(self): return self._new(itertools.chain.from_iterable(self.map(L)))
    def reduce(self, f, initial=None): return reduce(f, self) if initial is None else reduce(f, self, initial)
    def sum(self): return self.reduce(operator.add)
    def product(self): return self.reduce(operator.mul)
    def setattrs(self, attr, val): [setattr(o,attr,val) for o in self]

# Cell
add_docs(L,
         __getitem__="Retrieve `idx` (can be list of indices, or mask, or int) items",
         range="Class Method: Same as `range`, but returns `L`. Can pass collection for `a`, to use `len(a)`",
         split="Class Method: Same as `str.split`, but returns an `L`",
         copy="Same as `list.copy`, but returns an `L`",
         sorted="New `L` sorted by `key`. If key is str use `attrgetter`; if int use `itemgetter`",
         unique="Unique items, in stable order",
         val2idx="Dict from value to index",
         filter="Create new `L` filtered by predicate `f`, passing `args` and `kwargs` to `f`",
         argwhere="Like `filter`, but return indices for matching items",
         map="Create new `L` with `f` applied to all `items`, passing `args` and `kwargs` to `f`",
         map_first="First element of `map_filter`",
         map_dict="Like `map`, but creates a dict from `items` to function results",
         starmap="Like `map`, but use `itertools.starmap`",
         itemgot="Create new `L` with item `idx` of all `items`",
         attrgot="Create new `L` with attr `k` (or value `k` for dicts) of all `items`.",
         cycle="Same as `itertools.cycle`",
         enumerate="Same as `enumerate`",
         renumerate="Same as `renumerate`",
         zip="Create new `L` with `zip(*items)`",
         zipwith="Create new `L` with `self` zip with each of `*rest`",
         map_zip="Combine `zip` and `starmap`",
         map_zipwith="Combine `zipwith` and `starmap`",
         concat="Concatenate all elements of list",
         shuffle="Same as `random.shuffle`, but not inplace",
         reduce="Wrapper for `functools.reduce`",
         sum="Sum of the items",
         product="Product of the items",
         setattrs="Call `setattr` on all items"
        )

# Cell
#hide
L.__signature__ = pickle.loads(b'\x80\x03cinspect\nSignature\nq\x00(cinspect\nParameter\nq\x01X\x05\x00\x00\x00itemsq\x02cinspect\n_ParameterKind\nq\x03K\x01\x85q\x04Rq\x05\x86q\x06Rq\x07}q\x08(X\x08\x00\x00\x00_defaultq\tNX\x0b\x00\x00\x00_annotationq\ncinspect\n_empty\nq\x0bubh\x01X\x04\x00\x00\x00restq\x0ch\x03K\x02\x85q\rRq\x0e\x86q\x0fRq\x10}q\x11(h\th\x0bh\nh\x0bubh\x01X\x08\x00\x00\x00use_listq\x12h\x03K\x03\x85q\x13Rq\x14\x86q\x15Rq\x16}q\x17(h\t\x89h\nh\x0bubh\x01X\x05\x00\x00\x00matchq\x18h\x14\x86q\x19Rq\x1a}q\x1b(h\tNh\nh\x0bubtq\x1c\x85q\x1dRq\x1e}q\x1fX\x12\x00\x00\x00_return_annotationq h\x0bsb.')

# Cell
Sequence.register(L);

# Cell
def save_config_file(file, d, **kwargs):
    "Write settings dict to a new config file, or overwrite the existing one."
    config = ConfigParser(**kwargs)
    config['DEFAULT'] = d
    config.write(open(file, 'w'))

# Cell
def read_config_file(file, **kwargs):
    config = ConfigParser(**kwargs)
    config.read(file)
    return config

# Cell
def _add_new_defaults(cfg, file, **kwargs):
    for k,v in kwargs.items():
        if cfg.get(k, None) is None:
            cfg[k] = v
            save_config_file(file, cfg)

# Cell
@lru_cache(maxsize=None)
class Config:
    "Reading and writing `settings.ini`"
    def __init__(self, cfg_name='settings.ini'):
        cfg_path = Path.cwd()
        while cfg_path != cfg_path.parent and not (cfg_path/cfg_name).exists(): cfg_path = cfg_path.parent
        self.config_path,self.config_file = cfg_path,cfg_path/cfg_name
        assert self.config_file.exists(), f"Could not find {cfg_name}"
        self.d = read_config_file(self.config_file)['DEFAULT']
        _add_new_defaults(self.d, self.config_file,
                         host="github", doc_host="https://%(user)s.github.io", doc_baseurl="/%(lib_name)s/")

    def __setitem__(self,k,v): self.d[k] = str(v)
    def __contains__(self,k):  return k in self.d
    def save(self):            save_config_file(self.config_file,self.d)
    def __getattr__(self,k):   return stop(AttributeError(k)) if k=='d' or k not in self.d else self.get(k)
    def get(self,k,default=None): return self.d.get(k, default)
    def path(self,k,default=None):
        v = self.get(k, default)
        return v if v is None else self.config_path/v