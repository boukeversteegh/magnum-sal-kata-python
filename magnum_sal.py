from collections import Counter

from events import ChamberAdded, MinerPlaced, MinerRemoved, Events


class ApplicationException(Exception):
  pass


class MagnumSal:
  def __init__(self, events: Events):
    neighbor_view = NeighborView(events)
    self.events = events
    self.miner_placement_service = MinerPlacementService(events, neighbor_view)
    self.miner_removal_service = MinerRemovalService(events, neighbor_view)

  def add_chamber(self, x, y):
    self.events.append(ChamberAdded(x, y))
    pass


class NeighborView:
  def __init__(self, events: Events):
    self.events = events

  def get_neighbors(self, x, y):

    def is_neighbor(a):
      return abs(a.x - x) + abs(a.y - y) == 1

    neighbors_placed = Counter(self.events.filter(MinerPlaced, is_neighbor, as_tuple=('x', 'y')))
    neighbors_removed = Counter(self.events.filter(MinerRemoved, is_neighbor, as_tuple=('x', 'y')))
    neighbors = neighbors_placed - neighbors_removed
    return neighbors


class MinerPlacementService:
  def __init__(self, events, neighbor_view: NeighborView):
    self.neighbor_view = neighbor_view
    self.events = events

  def place_miner(self, x, y):
    # is there a chamber at x, y?
    chambers = self.events.filter(ChamberAdded, x=x, y=y)
    if not chambers:
      raise ApplicationException(
        "There was no chamber at %s, %s, so you cannot place a miner there" % (x, y)
      )

    # if not at start, is there a neighboring miner near x, y?
    neighbors = self.neighbor_view.get_neighbors(x, y)

    if (x, y) != (0, 0) and not neighbors:
      raise ApplicationException(
        "You cannot place a miner at [%s, %s] because there are no neighbors there" % (x, y)
      )

    self.events.append(MinerPlaced(x, y))


class MinerRemovalService:
  def __init__(self, events, neighbor_view: NeighborView):
    self.neighbor_view = neighbor_view
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
    neighbors = self.neighbor_view.get_neighbors(x, y)
    in_chain = len(neighbors) == 2 or (x, y) == (0, 0) and len(neighbors) == 1

    if in_chain and miners_there == 1:
      raise ApplicationException("You cannot remove a miner from the middle of a chain at [%s, %s]" % (x, y))

    events.append(MinerRemoved(x, y))
