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
    events = self.events

    # is there a miner at x, y
    miners_placed_there = events.filter(MinerPlaced, lambda e: e.x == x and e.y == y)

    if not miners_placed_there:
      raise ApplicationException("There was no miner to be removed at [%s, %s]" % (x, y))

    miners_removed_there = [mp for mp in events if isinstance(mp, MinerRemoved) and mp.x == x and mp.y == y]

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
      n_miners_placed = [mp for mp in events if
                         isinstance(mp, MinerPlaced) and mp.x == x + ndx and mp.y == y + ndy]
      n_miners_removed = [mr for mr in events if
                          isinstance(mr, MinerRemoved) and mr.x == x + ndx and mr.y == y + ndy]
      n_has_neighbor = len(n_miners_placed) - len(n_miners_removed) > 0

      if n_has_neighbor:
        chambers_with_neighbors += 1

    in_chain = chambers_with_neighbors == 2 or (x, y) == (0, 0) and chambers_with_neighbors == 1

    if in_chain and miners_there == 1:
      raise ApplicationException("You cannot remove a miner from the middle of a chain at [%s, %s]" % (x, y))

    events.append(MinerRemoved(x, y))


