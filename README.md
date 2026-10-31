# Multi-Planar-Medical-Image-Reconstruction

Multi-planar reconstruction (MPR) in C++ with **VTK 9**: from one 3D volume, extract the **axial, coronal, sagittal** and an **oblique** slice using `vtkImageReslice`.

> Status: example code, not validated on clinical data. Not for clinical use.

## Result (synthetic test volume)
`mpr_result.png`: axial | coronal | sagittal | oblique. The test volume is 96 x 96 x 64 voxels with spacing 1 x 1 x 2 mm, containing an ellipsoid, a bright sphere and a box. The slices show the expected shapes, and the sphere appears at the correct side and height in the coronal view. No patient data is used.

## Build and run
```
mkdir build && cd build
cmake .. && make
./mpr_slicer                    # synthetic volume
./mpr_slicer path/to/dicom_dir  # your own DICOM series (folder)
```
Requires VTK 9 and CMake. Tested with VTK 9.1. Output: `axial.png`, `coronal.png`, `sagittal.png`, `oblique.png`.

## How it works
1. Load a DICOM series (`vtkDICOMImageReader`) or build a test volume.
2. Define each plane by a 4x4 matrix: the columns are the plane axes and the centre of the volume.
3. Reslice with linear interpolation (`vtkImageReslice`), scale to 8 bit and write PNG.

## Notes
- With a real DICOM series, image orientation is not corrected yet: the code uses the voxel axes, not the patient coordinate system.
- Never upload patient DICOM data to a public repository.

## Use and contact
If you use, adapt or contribute to this work, please credit the author and **contact or inform me by email: owaiskhan_bangash@yahoo.com**

## Author
BEN, Software Engineer. GitHub: [Bangash514](https://github.com/Bangash514)
