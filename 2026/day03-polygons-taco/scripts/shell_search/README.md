# Taco shell, closed-dome search (3 Nov)
Scripts: 01_dome.py (pool + discriminative scoring; ~4 min, 7 procs), 03_rescore.py (adds arc-corner test, detail floor, filters), 04_deliver.py (CSV, sheet, top-3 silhouettes; arg = 0-based ranks).
Pool: 60,518 units (NE admin-0/admin-1/islands/minor islands/lakes x3, geoBoundaries CGAZ ADM2, US Census 2023 cb counties + places 1:500k). 9,705 passed shape prefilters + dome IoU>=0.80; 161 pass margin>0.03, base dev<=10%, W:H 1.4-2.6, >=12 arc vertices.
Score = IoU(half-ellipse, A 1.6-2.2, 5°+1° rotations) + margin(IoU - best rect/full-ellipse IoU, A 1.0-3.0) - 3*max(0, base_dev-3%) - 0.5*(1-arc convexity) - 0.3*(1-arc monotonic turning) - 0.8*max(0, arc corner share-0.25).
Caveat: CGAZ ADM2 is heavily simplified, so many CGAZ "domes" are really coarse trapezoids.
