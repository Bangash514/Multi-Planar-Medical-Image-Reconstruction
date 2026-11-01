# BEN 2026-11-01
# Change aim: multi-planar reconstruction with ITK 5 (ResampleImageFilter) in Python.
# File: mpr_itk.py
# Usage: python3 python/mpr_itk.py   (writes results/py_itk.png and results/py_itk.npz)
import os
import numpy as np
import itk

import mpr_common as c


def reslice(img, axes):
    ImageT = type(img)
    origin = c.CENTRE - 0.5 * c.SIZE * axes[:, 0] - 0.5 * c.SIZE * axes[:, 1]
    f = itk.ResampleImageFilter[ImageT, ImageT].New()
    f.SetInput(img)
    f.SetSize([c.SIZE, c.SIZE, 1])
    f.SetOutputSpacing([1.0, 1.0, 1.0])
    f.SetOutputOrigin([float(v) for v in origin])
    f.SetOutputDirection(itk.matrix_from_array(np.ascontiguousarray(axes, dtype=np.float64)))
    f.SetDefaultPixelValue(0.0)
    f.SetInterpolator(itk.LinearInterpolateImageFunction[ImageT, itk.D].New())
    f.Update()
    return itk.array_from_image(f.GetOutput())[0].astype(np.float32)


def main():
    img = itk.image_from_array(c.make_volume())
    img.SetSpacing([float(s) for s in c.SPACING])
    img.SetOrigin([0.0, 0.0, 0.0])
    out = {name: reslice(img, ax) for name, ax in c.planes().items()}
    os.makedirs("results", exist_ok=True)
    np.savez("results/py_itk.npz", **out)
    c.save_montage(out, "results/py_itk.png", "ITK " + itk.Version.GetITKVersion())
    print("ITK", itk.Version.GetITKVersion(), "-> results/py_itk.png")


if __name__ == "__main__":
    main()
