# BEN 2026-11-01
# Change aim: multi-planar reconstruction with OpenCV only: trilinear sampling built from cv2.remap on each z slice.
# File: mpr_opencv.py
# Usage: python3 python/mpr_opencv.py   (writes results/py_opencv.png and results/py_opencv.npz)
import os
import numpy as np
import cv2

import mpr_common as c


def reslice(vol, axes):
    u = np.arange(c.SIZE, dtype=np.float64) - 0.5 * c.SIZE
    uu, vv = np.meshgrid(u, u)                                   # rows = v, cols = u
    pts = [c.CENTRE[i] + axes[i, 0] * uu + axes[i, 1] * vv for i in range(3)]   # physical x, y, z in mm
    fx = (pts[0] / c.SPACING[0]).astype(np.float32)
    fy = (pts[1] / c.SPACING[1]).astype(np.float32)
    fz = pts[2] / c.SPACING[2]
    out = np.zeros((c.SIZE, c.SIZE), np.float32)
    for k in range(c.NZ):
        w = np.clip(1.0 - np.abs(fz - k), 0.0, None).astype(np.float32)   # linear weight along z
        if not w.any():
            continue
        s = cv2.remap(vol[k], fx, fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        out += w * s
    return out


def main():
    vol = c.make_volume()
    out = {name: reslice(vol, ax) for name, ax in c.planes().items()}
    os.makedirs("results", exist_ok=True)
    np.savez("results/py_opencv.npz", **out)
    c.save_montage(out, "results/py_opencv.png", "OpenCV " + cv2.__version__)
    print("OpenCV", cv2.__version__, "-> results/py_opencv.png")


if __name__ == "__main__":
    main()
