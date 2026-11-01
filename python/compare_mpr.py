# BEN 2026-11-01
# Change aim: compare the VTK, ITK and OpenCV slices pixel by pixel on the same synthetic volume.
# File: compare_mpr.py
# Usage: python3 python/compare_mpr.py   (run the three mpr_*.py scripts first)
import itertools
import numpy as np

names = ["vtk", "itk", "opencv"]
data = {n: np.load(f"results/py_{n}.npz") for n in names}
lines = ["pair | plane | mean abs diff (gray levels) | max abs diff | pixels differing by more than 5 (%)"]
for a, b in itertools.combinations(names, 2):
    for p in ("axial", "coronal", "sagittal", "oblique"):
        d = np.abs(data[a][p].astype(np.float64) - data[b][p].astype(np.float64))
        lines.append(f"{a}-{b} | {p} | {d.mean():.3f} | {d.max():.3f} | {100.0 * (d > 5).mean():.2f}")
open("results/py_compare.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
