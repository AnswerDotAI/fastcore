# Docments


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

[`docments`](https://fastcore.fast.ai/docments.html#docments) provides
programmatic access to comments in function parameters and return types.
It can be used to create more developer-friendly documentation, CLI, etc
tools.

## Why?

Without docments, if you want to document your parameters, you have to
repeat param names in docstrings, since they’re already in the function
signature. The parameters have to be kept synchronized in the two places
as you change your code. Readers of your code have to look back and
forth between two places to understand what’s happening. So it’s more
work for you, and for your users.

Furthermore, to have parameter documentation formatted nicely without
docments, you have to use special magic docstring formatting, often with
[odd
quirks](https://stackoverflow.com/questions/62167540/why-do-definitions-have-a-space-before-the-colon-in-numpy-docstring-sections),
which is a pain to create and maintain, and awkward to read in code. For
instance, using [numpy-style
documentation](https://numpydoc.readthedocs.io/en/latest/format.html):

``` python
def add_np(a:int, b:int=0)->int:
    """The sum of two numbers.
    
    Used to demonstrate numpy-style docstrings.

Parameters
----------
a : int
    the 1st number to add
b : int
    the 2nd number to add (default: 0)

Returns
-------
int
    the result of adding `a` to `b`"""
    return a+b
```

By comparison, here’s the same thing using docments:

``` python
def add(
    a:int, # the 1st number to add
    b=0,   # the 2nd number to add
)->int:    # the result of adding `a` to `b`
    "The sum of two numbers."
    return a+b
```

## Numpy docstring helper functions

[`docments`](https://fastcore.fast.ai/docments.html#docments) also
supports numpy-style docstrings, or a mix or numpy-style and docments
parameter documentation. The functions in this section help get and
parse this information.

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L26"
target="_blank" style="float:right; font-size:smaller">source</a>

### docstring

>  docstring (sym)

*Get docstring for `sym` for functions ad classes*

``` python
test_eq(docstring(add), "The sum of two numbers.")
```

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L34"
target="_blank" style="float:right; font-size:smaller">source</a>

### parse_docstring

>  parse_docstring (sym)

*Parse a numpy-style docstring in `sym`*

``` python
# parse_docstring(add_np)
```

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L39"
target="_blank" style="float:right; font-size:smaller">source</a>

### isdataclass

>  isdataclass (s)

*Check if `s` is a dataclass but not a dataclass’ instance*

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L44"
target="_blank" style="float:right; font-size:smaller">source</a>

### get_dataclass_source

>  get_dataclass_source (s)

*Get source code for dataclass `s`*

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L49"
target="_blank" style="float:right; font-size:smaller">source</a>

### get_source

>  get_source (s)

*Get source code for string, function object or dataclass `s`*

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L126"
target="_blank" style="float:right; font-size:smaller">source</a>

### get_name

>  get_name (obj)

*Get the name of `obj`*

``` python
test_eq(get_name(in_ipython), 'in_ipython')
test_eq(get_name(L.map), 'map')
```

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L135"
target="_blank" style="float:right; font-size:smaller">source</a>

### qual_name

>  qual_name (obj)

*Get the qualified name of `obj`*

``` python
assert qual_name(docscrape) == 'fastcore.docscrape'
```

## Docments

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L162"
target="_blank" style="float:right; font-size:smaller">source</a>

### docments

>  docments (elt, full=False, returns=True, eval_str=False,
>                args_kwargs=False)

*Generates a `docment`*

The returned `dict` has parameter names as keys, docments as values. The
return value comment appears in the `return`, unless `returns=False`.
Using the `add` definition above, we get:

``` python
def add(
    a:int, # the 1st number to add
    b=0,   # the 2nd number to add
)->int:    # the result of adding `a` to `b`
    "The sum of two numbers."
    return a+b

docments(add)
```

``` json
{ 'a': 'the 1st number to add',
  'b': 'the 2nd number to add',
  'return': 'the result of adding `a` to `b`'}
```

``` python
def add(*args, # some args
    a:int, # the 1st number to add
    b=0,   # the 2nd number to add
    **kwargs, # Passed to the `example` function
)->int:    # the result of adding `a` to `b`
    "The sum of two numbers."
    return a+b

docments(add, args_kwargs=True)
```

``` json
{ 'a': 'the 1st number to add',
  'args': 'some args',
  'b': 'the 2nd number to add',
  'kwargs': 'Passed to the `example` function',
  'return': 'the result of adding `a` to `b`'}
```

If you pass `full=True`, the values are `dict` of defaults, types, and
docments as values. Note that the type annotation is inferred from the
default value, if the annotation is empty and a default is supplied.

``` python
docments(add, full=True)
```

``` json
{ 'a': { 'anno': <class 'int'>,
         'default': <class 'inspect._empty'>,
         'docment': 'the 1st number to add'},
  'b': { 'anno': <class 'int'>,
         'default': 0,
         'docment': 'the 2nd number to add'},
  'return': { 'anno': <class 'int'>,
              'default': <class 'inspect._empty'>,
              'docment': 'the result of adding `a` to `b`'}}
```

To evaluate stringified annotations (from python 3.10), use `eval_str`:

``` python
docments(add, full=True, eval_str=True)['a']
```

``` json
{ 'anno': <class 'int'>,
  'default': <class 'inspect._empty'>,
  'docment': 'the 1st number to add'}
```

If you need more space to document a parameter, place one or more lines
of comments above the parameter, or above the return type. You can
mix-and-match these docment styles:

``` python
def add(
    # The first operand
    a:int,
    # This is the second of the operands to the *addition* operator.
    # Note that passing a negative value here is the equivalent of the *subtraction* operator.
    b:int,
)->int: # The result is calculated using Python's builtin `+` operator.
    "Add `a` to `b`"
    return a+b
```

``` python
docments(add)
```

``` json
{ 'a': 'The first operand',
  'b': 'This is the second of the operands to the *addition* operator.\n'
       'Note that passing a negative value here is the equivalent of the '
       '*subtraction* operator.',
  'return': "The result is calculated using Python's builtin `+` operator."}
```

Docments works with async functions, too:

``` python
async def add_async(
    # The first operand
    a:int,
    # This is the second of the operands to the *addition* operator.
    # Note that passing a negative value here is the equivalent of the *subtraction* operator.
    b:int,
)->int: # The result is calculated using Python's builtin `+` operator.
    "Add `a` to `b`"
    return a+b
```

``` python
test_eq(docments(add_async), docments(add))
```

You can also use docments with classes and methods:

``` python
class Adder:
    "An addition calculator"
    def __init__(self,
        a:int, # First operand
        b:int, # 2nd operand
    ): self.a,self.b = a,b
    
    def calculate(self
                 )->int: # Integral result of addition operator
        "Add `a` to `b`"
        return a+b
```

``` python
docments(Adder)
```

``` json
{'a': 'First operand', 'b': '2nd operand', 'return': None}
```

``` python
docments(Adder.calculate)
```

``` json
{'return': 'Integral result of addition operator', 'self': None}
```

docments can also be extracted from numpy-style docstrings:

``` python
print(add_np.__doc__)
```

    The sum of two numbers.
        
        Used to demonstrate numpy-style docstrings.

    Parameters
    ----------
    a : int
        the 1st number to add
    b : int
        the 2nd number to add (default: 0)

    Returns
    -------
    int
        the result of adding `a` to `b`

``` python
docments(add_np)
```

``` json
{ 'a': 'the 1st number to add',
  'b': 'the 2nd number to add (default: 0)',
  'return': 'the result of adding `a` to `b`'}
```

You can even mix and match docments and numpy parameters:

``` python
def add_mixed(a:int, # the first number to add
              b
             )->int: # the result
    """The sum of two numbers.

Parameters
----------
b : int
    the 2nd number to add (default: 0)"""
    return a+b
```

``` python
docments(add_mixed, full=True)
```

``` json
{ 'a': { 'anno': <class 'int'>,
         'default': <class 'inspect._empty'>,
         'docment': 'the first number to add'},
  'b': { 'anno': 'int',
         'default': <class 'inspect._empty'>,
         'docment': 'the 2nd number to add (default: 0)'},
  'return': { 'anno': <class 'int'>,
              'default': <class 'inspect._empty'>,
              'docment': 'the result'}}
```

You can use docments with dataclasses, however if the class was defined
in online notebook, docments will not contain parameters’ comments. This
is because the source code is not available in the notebook. After
converting the notebook to a module, the docments will be available.
Thus, documentation will have correct parameters’ comments.

Docments even works with
[`delegates`](https://fastcore.fast.ai/meta.html#delegates):

``` python
from fastcore.meta import delegates
```

``` python
def _a(a:int=2): return a # First

@delegates(_a)
def _b(b:str, # Second
       **kwargs): 
    return b, (_a(**kwargs)) 

docments(_b)
```

``` json
{'a': 'First', 'b': 'Second', 'return': None}
```

``` python
def _a(a:int=2): return a # First

@delegates(_a)
def _b(b:str, # Second
       **kwargs): 
    return b, (_a(**kwargs)) 
docments(_b)
```

``` json
{'a': 'First', 'b': 'Second', 'return': None}
```

## Extract docstrings

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/fastcore/blob/master/fastcore/docments.py#L215"
target="_blank" style="float:right; font-size:smaller">source</a>

### extract_docstrings

>  extract_docstrings (code)

*Create a dict from function/class/method names to tuples of docstrings
and param lists*

``` python
sample_code = """
"This is a module."

def top_func(a, b, *args, **kw):
    "This is top-level."
    pass

class SampleClass:
    "This is a class."

    def __init__(self, x, y):
        "Constructor for SampleClass."
        pass

    def method1(self, param1):
        "This is method1."
        pass

    def _private_method(self):
        "This should not be included."
        pass

class AnotherClass:
    def __init__(self, a, b):
        "This class has no separate docstring."
        pass"""

exp = {'_module': ('This is a module.', ''),
       'top_func': ('This is top-level.', 'a, b, *args, **kw'),
       'SampleClass': ('This is a class.', 'self, x, y'),
       'SampleClass.method1': ('This is method1.', 'self, param1'),
       'AnotherClass': ('This class has no separate docstring.', 'self, a, b')}
test_eq(extract_docstrings(sample_code), exp)
```