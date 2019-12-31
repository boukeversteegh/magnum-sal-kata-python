import unittest

from events import ChamberAdded, MinerPlaced, MinerRemoved, Events
from magnum_sal import MagnumSal, ApplicationException


class Tests(unittest.TestCase):

  def test_init_world(self):
    events = Events([])
    game = MagnumSal(events)

    game.add_chamber(0, 0)

    self.assertEqual([ChamberAdded(0, 0)], events)

  # Placing miners

  def test_place_miner_at_start_of_mine(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
    ])

    game = MagnumSal(events)

    game.miner_placement_service.place_miner(0, 0)

    self.assertIn(MinerPlaced(0, 0), events)

  def test_we_cannot_place_a_miner_outside_of_a_chamber(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
    ])

    game = MagnumSal(events)

    self.assertRaises(ApplicationException, lambda: game.miner_placement_service.place_miner(-1, 0))
    self.assertNotIn(MinerPlaced(-1, 0), events)
    self.assertEqual([], events.filter(MinerPlaced))

  def test_we_cannot_place_a_miner_somewhere_without_neighbors(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
    ])

    game = MagnumSal(events)

    self.assertRaises(
      ApplicationException, lambda: game.miner_placement_service.place_miner(0, 2))
    self.assertNotIn(MinerPlaced(0, 2), events)

  def test_we_place_a_miner_deeply_in_the_shaft_next_to_a_neighbor(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      ChamberAdded(1, 2),
      MinerPlaced(0, 1),
      MinerPlaced(0, 2),
    ])

    game = MagnumSal(events)

    game.miner_placement_service.place_miner(1, 2)
    self.assertIn(MinerPlaced(1, 2), events)

  # Removing Miners

  def test_we_can_remove_the_first_miner(self):
    events = Events([
      ChamberAdded(0, 0),
      MinerPlaced(0, 0),
    ])

    game = MagnumSal(events)

    game.miner_removal_service.remove_miner(0, 0)

    self.assertIn(MinerRemoved(0, 0), events)

  def test_we_cannot_remove_a_non_existent_miner(self):
    events = Events([
      ChamberAdded(0, 0),
    ])

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 0))
    self.assertEqual([], events.filter(MinerRemoved))

  def test_we_cannot_remove_a_previously_removed_miner(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerRemoved(0, 1),
    ])

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 1))
    self.assertEqual([MinerRemoved(0, 1)], events.filter(MinerRemoved))

  def test_we_can_remove_a_removed_and_readded_miner(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerRemoved(0, 1),
      MinerPlaced(0, 1),
    ])

    game = MagnumSal(events)

    game.miner_removal_service.remove_miner(0, 1)

    self.assertEqual([MinerRemoved(0, 1), MinerRemoved(0, 1)], events.filter(MinerRemoved))

  def test_we_can_remove_the_last_miner_in_a_chain(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerPlaced(-1, 1),
      MinerPlaced(0, 2),
    ])

    game = MagnumSal(events)

    game.miner_removal_service.remove_miner(-1, 1)

    self.assertIn(MinerRemoved(-1, 1), events.filter(MinerRemoved))

  def test_we_cannot_remove_a_neighbor_in_the_middle_of_a_chain(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerPlaced(0, 2),
    ])

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 1))

    self.assertNotIn(MinerRemoved(0, 1), events.filter(MinerRemoved))

  def test_we_can_remove_a_neighbor_in_the_middle_of_a_chain_if_the_chain_does_not_break(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerPlaced(0, 1),
      MinerPlaced(0, 2),
    ])

    game = MagnumSal(events)

    game.miner_removal_service.remove_miner(0, 1)

    self.assertEqual([MinerRemoved(0, 1)], events.filter(MinerRemoved))

  def test_we_cannot_remove_a_neighbor_in_the_middle_of_a_chain_if_the_chain_breaks_with_removals_taken_into_account(
      self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerPlaced(0, 1),
      MinerPlaced(0, 2),
      MinerRemoved(0, 1),
    ])

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 1))

    self.assertEqual([MinerRemoved(0, 1)], events.filter(MinerRemoved))

  def test_we_cannot_remove_first_miner_if_there_is_a_second_miner(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
    ])

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_removal_service.remove_miner(0, 0))

  def test_cannot_place_a_miner_after_a_chamber_where_the_last_miner_was_removed(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerRemoved(0, 1),
    ])

    game = MagnumSal(events)

    self.assertRaises(ApplicationException,
                      lambda: game.miner_placement_service.place_miner(0, 2))

  def test_can_place_a_miner_after_a_chamber_where_the_last_miner_was_replaced(self):
    events = Events([
      ChamberAdded(0, 0),
      ChamberAdded(0, 1),
      ChamberAdded(0, 2),
      MinerPlaced(0, 0),
      MinerPlaced(0, 1),
      MinerRemoved(0, 1),
      MinerPlaced(0, 1),
    ])

    game = MagnumSal(events)

    game.miner_placement_service.place_miner(0, 2)

    self.assertIn(MinerPlaced(0, 2), events)
