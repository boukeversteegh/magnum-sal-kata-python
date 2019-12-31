from collections import Counter

from events import ChamberAdded, MinerPlaced, MinerRemoved, Events


class ApplicationException(Exception):
  pass


class MagnumSal:
  def __init__(self, events: Events):
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
    chambers = self.events.filter(ChamberAdded, x=x, y=y)
    if not chambers:
      raise ApplicationException(
        "There was no chamber at %s, %s, so you cannot place a miner there" % (x, y)
      )

    def manhattan(a, x, y):
      return abs(a.x - x) + abs(a.y - y)

    def is_neighbor(a):
      return manhattan(a, x, y) == 1

    # if not at start, is there a neighboring miner near x, y?
    neighbors_placed = self.events.filter(MinerPlaced, is_neighbor, as_tuple=('x', 'y'))
    neighbors_removed = self.events.filter(MinerRemoved, is_neighbor, as_tuple=('x', 'y'))

    neighbors_placed_count = Counter(neighbors_placed)
    neighbors_removed_count = Counter(neighbors_removed)

    neighbors_left = neighbors_placed_count - neighbors_removed_count

    if (x, y) != (0, 0) and not neighbors_left:
      raise ApplicationException(
        "You cannot place a miner at [%s, %s] because there are no neighbors there" % (x, y)
      )

    self.events.append(MinerPlaced(x, y))


class MinerRemovalService:
  def __init__(self, events):
    self.events = events

  def remove_miner(self, x, y):
    events = self.events

    # is there a miner at x, y
    miners_placed_there = events.filter(MinerPlaced, x=x, y=y)

    if not miners_placed_there:
      raise ApplicationException("There was no miner to be removed at [%s, %s]" % (x, y))

    miners_removed_there = events.filter(MinerRemoved, x=x, y=y)

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
      n_miners_placed = events.filter(MinerPlaced, x=x + ndx, y=y + ndy)
      n_miners_removed = events.filter(MinerRemoved, x=x + ndx, y=y + ndy)
      n_has_neighbor = len(n_miners_placed) - len(n_miners_removed) > 0

      if n_has_neighbor:
        chambers_with_neighbors += 1

    in_chain = chambers_with_neighbors == 2 or (x, y) == (0, 0) and chambers_with_neighbors == 1

    if in_chain and miners_there == 1:
      raise ApplicationException("You cannot remove a miner from the middle of a chain at [%s, %s]" % (x, y))

    events.append(MinerRemoved(x, y))


