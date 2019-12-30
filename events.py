from collections import namedtuple

ChamberAdded = namedtuple('ChamberAdded', ['x', 'y'])

MinerPlaced = namedtuple('MinerPlaced', ['x', 'y'])
MinerRemoved = namedtuple('MinerRemoved', ['x', 'y'])