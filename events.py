import unittest
from collections import namedtuple
from typing import List


def event(name, fields):
  def namedtuple_eq(self, other):
    return type(self) == type(other) and tuple.__eq__(self, other)

  new_tuple = namedtuple(name, fields)
  new_tuple.__eq__ = namedtuple_eq

  return new_tuple


ChamberAdded = event('ChamberAdded', ['x', 'y'])
MinerPlaced = event('MinerPlaced', ['x', 'y'])
MinerRemoved = event('MinerRemoved', ['x', 'y'])




class Events(List):
  def __init__(self, events=None):
    if events is None:
      events = []
    super().__init__(events)

  def append(self, event):
    super().append(event)

  def filter(self, event_type=None, cb=None, as_tuple=None, **kwargs):
    def apply_property_filters(e):
      for key, value in kwargs.items():
        if getattr(e, key) != value:
          return False
      return True

    def _filter(e):
      return isinstance(e, event_type) and (not cb or cb(e)) and (not kwargs or apply_property_filters(e))

    return [e if not as_tuple else tuple(getattr(e, attribute) for attribute in as_tuple) for e in self.__iter__() if _filter(e)]

  def __contains__(self, item):
    return item in self.filter(type(item))


class EventsTest(unittest.TestCase):
  def test_contains(self):
    self.assertTrue(MinerPlaced(0, -1) in Events([MinerPlaced(0, -1)]))
    self.assertFalse(MinerPlaced(0, -1) in Events([MinerRemoved(0, -1)]))

  def test_filter(self):
    self.assertEqual([MinerPlaced(0, -1)], Events([MinerPlaced(0, -1), MinerRemoved(0, -1)]).filter(MinerPlaced))
    self.assertEqual([MinerRemoved(0, -1)], Events([MinerPlaced(0, -1), MinerRemoved(0, -1)]).filter(MinerRemoved))
    self.assertNotEqual([MinerPlaced(0, -1)], Events([MinerPlaced(0, -1), MinerRemoved(0, -1)]).filter(MinerRemoved))

  def test_filter_properties(self):
    self.assertEqual([MinerPlaced(0, 0)], Events([MinerPlaced(0, -1), MinerPlaced(0, 0)]).filter(MinerPlaced, x=0, y=0))
