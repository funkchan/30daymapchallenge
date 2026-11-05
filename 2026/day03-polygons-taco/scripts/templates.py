"""Ingredient templates, unit area, centroid at origin, drawn upright as they would sit in the taco."""
import numpy as np, shapely
from shapely import affinity
from common import norm

def _circ(x, y, r): return shapely.Point(x, y).buffer(r, 64)

def shell(r_in=0.62):  # open taco shell seen end-on: U band opening upward
    a = np.linspace(np.pi, 2 * np.pi, 180)
    return norm(shapely.Polygon(np.r_[np.c_[np.cos(a), np.sin(a)], np.c_[r_in * np.cos(a[::-1]), r_in * np.sin(a[::-1])]]))

def drumstick():  # meaty bulb + tapering shaft + knuckle, horizontal
    meat = affinity.scale(_circ(0, 0, 1), 1.25, 1)
    shaft = shapely.Polygon([(0.8, 0.5), (2.9, 0.18), (2.9, -0.18), (0.8, -0.5)])
    knob = shapely.union_all([_circ(3.0, 0.22, 0.24), _circ(3.0, -0.22, 0.24)])
    return norm(shapely.union_all([meat, shaft, knob]))

def chorizo(bend=70, aspect=4.5):  # curved sausage, rounded ends
    R = 3.0; th = np.radians(np.linspace(90 - bend / 2, 90 + bend / 2, 60))
    arc = shapely.LineString(np.c_[R * np.cos(th), R * np.sin(th)])
    return norm(arc.buffer(arc.length / aspect / 2, 32))

def leaf(aspect=1.7):  # ovate leaf, pointed tip up
    t = np.linspace(0, 2 * np.pi, 240); x = np.sin(t) * (1 - 0.25 * np.cos(t)); y = -np.cos(t) * aspect
    return norm(shapely.Polygon(np.c_[x, y]).buffer(0))

def cilantro():  # trilobed leaf with short stalk
    lobes = [_circ(0, 0.95, 0.62), _circ(-0.78, 0.38, 0.55), _circ(0.78, 0.38, 0.55), _circ(0, 0.25, 0.55)]
    stalk = shapely.box(-0.06, -0.75, 0.06, 0)
    return norm(shapely.union_all(lobes + [stalk]))

def dollop():  # teardrop / swirl-tip dollop, tip up
    return norm(shapely.convex_hull(shapely.union_all([_circ(0, 0, 1), shapely.Point(0, 2.1)])))

def square(): return norm(shapely.box(-1, -1, 1, 1))

TEMPLATES = {"shell": shell(), "drumstick": drumstick(), "chorizo": chorizo(), "leaf": leaf(), "cilantro": cilantro(), "dollop": dollop(), "square": square()}
DECOYS = [norm(affinity.scale(shapely.Point(0, 0).buffer(1, 64), a, 1)) for a in (1, 1.5, 2, 3, 4)] + \
         [norm(shapely.box(-a, -1, a, 1)) for a in (1, 1.5, 2, 3, 4)]

def cilantro_deep():  # cilantro leaflet: three well-separated rounded lobes on a short stalk (solidity ~0.65)
    lobes = [_circ(0, 1.15, 0.55), _circ(-0.95, 0.45, 0.5), _circ(0.95, 0.45, 0.5), _circ(0, 0.3, 0.42),
             shapely.box(-0.12, 0.3, 0.12, 1.0), affinity.rotate(shapely.box(-0.1, 0.3, 0.1, 1.0), 60, origin=(0, 0.3)),
             affinity.rotate(shapely.box(-0.1, 0.3, 0.1, 1.0), -60, origin=(0, 0.3))]
    stalk = shapely.box(-0.05, -0.6, 0.05, 0.3)
    return norm(shapely.union_all(lobes + [stalk]))
TEMPLATES["cilantro_deep"] = cilantro_deep()
