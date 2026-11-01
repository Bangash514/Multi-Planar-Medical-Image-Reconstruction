# BEN 2026-11-01
# Change aim: multi-planar reconstruction with VTK 9 (vtkImageReslice) in Python.
# File: mpr_vtk.py
# Usage: python3 python/mpr_vtk.py   (writes results/py_vtk.png and results/py_vtk.npz)
import os
import numpy as np
import vtk
from vtk.util import numpy_support

import mpr_common as c


def reslice(vol_vtk, axes):
    m = vtk.vtkMatrix4x4()
    m.Identity()
    for i in range(3):
        for j in range(3):
            m.SetElement(i, j, float(axes[i, j]))
        m.SetElement(i, 3, float(c.CENTRE[i]))
    r = vtk.vtkImageReslice()
    r.SetInputData(vol_vtk)
    r.SetOutputDimensionality(2)
    r.SetResliceAxes(m)
    r.SetInterpolationModeToLinear()
    r.SetOutputSpacing(1.0, 1.0, 1.0)
    r.SetOutputOrigin(-0.5 * c.SIZE, -0.5 * c.SIZE, 0.0)
    r.SetOutputExtent(0, c.SIZE - 1, 0, c.SIZE - 1, 0, 0)
    r.SetBackgroundLevel(0.0)
    r.Update()
    arr = numpy_support.vtk_to_numpy(r.GetOutput().GetPointData().GetScalars())
    return arr.reshape(c.SIZE, c.SIZE).astype(np.float32)


def main():
    vol = c.make_volume()
    img = vtk.vtkImageData()
    img.SetDimensions(c.NX, c.NY, c.NZ)
    img.SetSpacing(*c.SPACING)
    img.SetOrigin(0.0, 0.0, 0.0)
    img.GetPointData().SetScalars(numpy_support.numpy_to_vtk(vol.ravel(), deep=True, array_type=vtk.VTK_FLOAT))
    out = {name: reslice(img, ax) for name, ax in c.planes().items()}
    os.makedirs("results", exist_ok=True)
    np.savez("results/py_vtk.npz", **out)
    c.save_montage(out, "results/py_vtk.png", "VTK " + vtk.vtkVersion.GetVTKVersion())
    print("VTK", vtk.vtkVersion.GetVTKVersion(), "-> results/py_vtk.png")


if __name__ == "__main__":
    main()
