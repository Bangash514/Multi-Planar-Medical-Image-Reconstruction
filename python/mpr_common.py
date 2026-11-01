# BEN 2026-11-01
# Change aim: shared synthetic test volume and slice-plane definitions for the VTK, ITK and OpenCV multi-planar scripts.
# File: mpr_common.py
# Synthetic data only, no patient images. Volume array is indexed [z, y, x]. Units: millimetres.
import numpy as np
import cv2

NX, NY, NZ = 96, 96, 64
SPACING = (1.0, 1.0, 2.0)
SIZE = 160            # output slice is SIZE x SIZE pixels, 1 mm per pixel
CENTRE = np.array([0.5 * SPACING[i] * (n - 1) for i, n in enumerate((NX, NY, NZ))])


def make_volume():
    z, y, x = np.meshgrid(np.arange(NZ), np.arange(NY), np.arange(NX), indexing="ij")
    px, py, pz = x * 1.0, y * 1.0, z * 2.0
    v = np.zeros((NZ, NY, NX), np.float32)
    v[((px - 48) / 40) ** 2 + ((py - 48) / 30) ** 2 + ((pz - 64) / 50) ** 2 < 1.0] = 100.0   # body ellipsoid
    v[(px - 35) ** 2 + (py - 55) ** 2 + (pz - 50) ** 2 < 144.0] = 255.0                      # bright sphere
    v[(px > 58) & (px < 74) & (py > 30) & (py < 46) & (pz > 70) & (pz < 100)] = 180.0        # box
    return v


def rot_xy(deg_x, deg_y):
    a, b = np.radians(deg_x), np.radians(deg_y)
    rx = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    ry = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    return rx @ ry


def planes():
    # each plane: 3x3 matrix whose columns are the slice axes X, Y, Z in volume coordinates
    ex, ey, ez = np.array([1., 0, 0]), np.array([0, 1., 0]), np.array([0, 0, 1.])
    return {
        "axial": np.column_stack([ex, ey, ez]),
        "coronal": np.column_stack([ex, ez, -ey]),
        "sagittal": np.column_stack([ey, ez, ex]),
        "oblique": rot_xy(30.0, 20.0),
    }


def to_u8(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def save_montage(slices, path, title):
    tiles = []
    for name in ("axial", "coronal", "sagittal", "oblique"):
        t = cv2.cvtColor(to_u8(slices[name]), cv2.COLOR_GRAY2BGR)
        t = cv2.resize(t, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        cv2.putText(t, name, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)
        tiles.append(t)
    m = np.hstack(tiles)
    cv2.putText(m, title + "  (synthetic volume)", (6, m.shape[0] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(path, m)
