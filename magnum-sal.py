import unittest

from events import ChamberAdded, MinerPlaced


class ApplicationException(Exception):
  pass


class MagnumSal:
  def __init__(self, events):
    self.events = events
    self.miner_placement_service = MinerPlacementService(events)

  def add_chamber(self, x, y):
    self.events.append(ChamberAdded(x, y))
    pass


class MinerPlacementService:
  def __init__(self, events):
    self.events = events

  def place_miner(self, x, y):
    # is there a chamber at x, y?
    chambers = [e for e in self.events if isinstance(e, ChamberAdded) and e.x == x and e.y == y]
    if not chambers:
      raise ApplicationException(
        "There was no chamber at %s, %s, so you cannot place a miner there" % (x, y)
      )

    # if not at start, is there a neighboring miner near x, y?
    neighboring_miners = [mp for mp in self.events if
                          isinstance(mp, MinerPlaced) and abs(mp.x - x) + abs(mp.y - y) == 1]
    if (x, y) != (0, 0) and not neighboring_miners:
      raise ApplicationException(
        "You cannot place a miner at [%s, %s] because there are no neighbors there" % (x, y)
      )

    self.events.append(MinerPlaced(x, y))


class Tests(unittest.TestCase):

  def test_init_world(self):
    events = []
    game = MagnumSal(events)

    game.add_chamber(0, 0)

    self.assertEqual([ChamberAdded(0, 0)], events)

  def test_place_miner_at_start_of_mine(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
    ]
    game = MagnumSal(events)

    game.miner_placement_service.place_miner(0, 0)

    self.assertIn(MinerPlaced(0, 0), events)

  def test_we_cannot_place_a_miner_outside_of_a_chamber(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
    ]
    game = MagnumSal(events)

    self.assertRaises(ApplicationException, lambda: game.miner_placement_service.place_miner(-1, 0))
    self.assertNotIn(MinerPlaced(-1, 0), events)
    self.assertEqual([], [e for e in events if isinstance(e, MinerPlaced)])

  def test_we_cannot_place_a_miner_somewhere_without_neighbors(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
    ]
    game = MagnumSal(events)

    self.assertRaises(
      ApplicationException, lambda: game.miner_placement_service.place_miner(0, 2))
    self.assertNotIn(MinerPlaced(0, 2), [e for e in events if isinstance(e, MinerPlaced)])

  def test_we_place_a_miner_deeply_in_the_shaft_next_to_a_neighbor(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      ChamberAdded(1, 2),
      MinerPlaced(0, 1),
      MinerPlaced(0, 2),
    ]
    game = MagnumSal(events)

    game.miner_placement_service.place_miner(1, 2)
    self.assertIn(MinerPlaced(1, 2), [e for e in events if isinstance(e, MinerPlaced)])
