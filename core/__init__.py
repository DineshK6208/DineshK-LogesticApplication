"""
Monkey-patch for Django 4.2 + Python 3.14 compatibility.

Python 3.14 changed super() objects so they no longer have __dict__,
which breaks Django's BaseContext.__copy__() method that does copy(super()).
This patch replaces __copy__() with a compatible implementation.
"""
import sys

if sys.version_info >= (3, 14):
    from copy import copy
    from django.template.context import BaseContext, Context

    def _patched_base_copy(self):
        """
        Create a shallow copy without relying on copy(super()),
        which fails on Python 3.14.
        """
        duplicate = object.__new__(type(self))
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _patched_base_copy

    def _patched_context_copy(self):
        duplicate = _patched_base_copy(self)
        duplicate.render_context = copy(self.render_context)
        return duplicate

    Context.__copy__ = _patched_context_copy
