__all__ = ['f', 'g']
from fastcore.meta import delegates
from fastcore.utils import patch

class X(int):
    pass

def f(a: int, b: str='a') -> str:
    """I am f"""
    ...

def g(c, d: X, *, b: str='a') -> str:
    """I am g"""
    ...

def j(c: int, d: str='a') -> str:
    """I am j"""
    ...

class A:

    def h(self, b: bool=False, *, d: str='a'):
        ...

    def k(self, b: bool=False, *, d: str='a'):
        ...

    def m(self, b: bool=False, *, d: str='a'):
        ...

    def n(self, b: bool=False, **kwargs):
        """No delegates here mmm'k?"""
        ...

class B:

    def k(self, b: bool=False, *, d: str='a'):
        ...