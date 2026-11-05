"""Quick review grid: clean silhouettes in best (upright) rotation, no overlay."""
import os, sys, numpy as np, pandas as pd, shapely, geopandas as gpd
from shapely import affinity
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from common import local, norm, parts
def upright(g_ll, rot, main_only=True, flip=False):
    g = local(g_ll).buffer(0)
    if main_only: g = max(parts(g), key=lambda p: p.area)
    c = g.centroid; g = affinity.rotate(affinity.translate(g, -c.x, -c.y), -rot, origin=(0, 0))
    return affinity.rotate(g, 180, origin=(0, 0)) if flip else g
def grid(items, path, cols=6, title=""):
    rows = int(np.ceil(len(items) / cols)); fig, axs = plt.subplots(rows, cols, figsize=(cols * 2.6, rows * 2.9), dpi=100, facecolor="#F2EDDF")
    for ax in np.atleast_1d(axs).flat: ax.set_axis_off()
    for ax, (g, lab) in zip(np.atleast_1d(axs).flat, items):
        gpd.GeoSeries([g]).plot(ax=ax, color="#2A2620", lw=0.3, edgecolor="#2A2620"); ax.set_aspect("equal"); ax.set_title(lab, fontsize=7.5)
    fig.suptitle(title, fontsize=12); plt.tight_layout(); fig.savefig(path, facecolor="#F2EDDF"); plt.close(fig)
