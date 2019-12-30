import unittest

from events import ChamberAdded, MinerPlaced, MinerRemoved


class ApplicationException(Exception):
  pass


class MagnumSal:
  def __init__(self, events):
    self.events = events
    self.miner_placement_service = MinerPlacementService(events)
    self.miner_removal_service = MinerRemovalService(events)

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


class MinerRemovalService:
  def __init__(self, events):
    self.events = events

  def remove_miner(self, x, y):
    # is there a miner at x, y
    miners_placed_there = [mp for mp in self.events if isinstance(mp, MinerPlaced) and mp.x == x and mp.y == y]

    if not miners_placed_there:
      raise ApplicationException("There was no miner to be removed at [%s, %s]" % (x, y))

    miners_removed_there = [mp for mp in self.events if isinstance(mp, MinerRemoved) and mp.x == x and mp.y == y]

    # Are there miners left, after considering removals?
    miners_there = len(miners_placed_there) - len(miners_removed_there)
    if miners_there == 0:
      raise ApplicationException("All miners at [%s, %s] were already removed" % (x, y))

    # Do we not break the chain?
    neighbors_dxdy = [
      (-1, 0),
      (1, 0),
      (0, 1),
      (0, -1)
    ]

    chambers_with_neighbors = 0
    # if there are neighbors on 2 sides, then we're in the middle of a chain
    for ndx, ndy in neighbors_dxdy:
      n_miners_placed = [mp for mp in self.events if
                         isinstance(mp, MinerPlaced) and mp.x == x + ndx and mp.y == y + ndy]
      n_miners_removed = [mr for mr in self.events if
                          isinstance(mr, MinerRemoved) and mr.x == x + ndx and mr.y == y + ndy]
      n_has_neighbor = len(n_miners_placed) - len(n_miners_removed) > 0

      if n_has_neighbor:
        chambers_with_neighbors += 1

    in_chain = chambers_with_neighbors == 2

    if in_chain and miners_there == 1:
      raise ApplicationException("You cannot remove a miner from the middle of a chain at [%s, %s]" % (x, y))

    self.events.append(MinerRemoved(x, y))


class Tests(unittest.TestCase):

  def test_init_world(self):
    events = []
    game = MagnumSal(events)

    game.add_chamber(0, 0)

    self.assertEqual([ChamberAdded(0, 0)], events)

  # Placing miners

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

  # Removing Miners

  def test_we_can_remove_the_first_miner(self):
    events = [
      ChamberAdded(0, 0),
      MinerPlaced(0, 0),
    ]

    game = MagnumSal(events)

    game.miner_removal_service.remove_miner(0, 0)

    self.assertIn(MinerRemoved(0, 0), [e for e in events if isinstance(e, MinerRemoved)])

  def test_we_cannot_remove_a_non_existant_miner(self):
    events = [
      ChamberAdded(0, 0),
    ]

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 0))
    self.assertEquals([], [e for e in events if isinstance(e, MinerRemoved)])

  def test_we_cannot_remove_a_previously_removed_miner(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerRemoved(0, 1),
    ]

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 1))
    self.assertEquals([MinerRemoved(0, 1)], [e for e in events if isinstance(e, MinerRemoved)])

  def test_we_can_remove_a_removed_and_readded_miner(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerRemoved(0, 1),
      MinerPlaced(0, 1),
    ]

    game = MagnumSal(events)

    game.miner_removal_service.remove_miner(0, 1)

    self.assertEquals([MinerRemoved(0, 1), MinerRemoved(0, 1)], [e for e in events if isinstance(e, MinerRemoved)])

  def test_we_can_remove_the_last_miner_in_a_chain(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerPlaced(-1, 1),
      MinerPlaced(0, 2),
    ]

    game = MagnumSal(events)

    game.miner_removal_service.remove_miner(-1, 1)

    self.assertIn(MinerRemoved(-1, 1), [e for e in events if isinstance(e, MinerRemoved)])

  def test_we_cannot_remove_a_neighbor_in_the_middle_of_a_chain(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerPlaced(0, 2),
    ]

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 1))

    self.assertNotIn(MinerRemoved(0, 1), [e for e in events if isinstance(e, MinerRemoved)])

  def test_we_can_remove_a_neighbor_in_the_middle_of_a_chain_if_the_chain_does_not_break(self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerPlaced(0, 1),
      MinerPlaced(0, 2),
    ]

    game = MagnumSal(events)

    game.miner_removal_service.remove_miner(0, 1)

    self.assertEqual([MinerRemoved(0, 1)], [e for e in events if isinstance(e, MinerRemoved)])

  def test_we_cannot_remove_a_neighbor_in_the_middle_of_a_chain_if_the_chain_breaks_with_removals_taken_into_account(
      self):
    events = [
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerPlaced(0, 1),
      MinerPlaced(0, 2),
      MinerRemoved(0, 1),
    ]

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 1))

    self.assertEqual([MinerRemoved(0, 1)], [e for e in events if isinstance(e, MinerRemoved)])
