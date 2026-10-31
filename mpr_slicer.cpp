// BEN 2026-11-01
// Change aim: Extract axial, coronal, sagittal and oblique slices from a 3D volume with VTK 9.
// File: mpr_slicer.cpp
#include <vtkDICOMImageReader.h>
#include <vtkImageData.h>
#include <vtkImageReslice.h>
#include <vtkImageShiftScale.h>
#include <vtkMatrix4x4.h>
#include <vtkNew.h>
#include <vtkPNGWriter.h>
#include <vtkTransform.h>

#include <cmath>
#include <iostream>
#include <string>

// BEN 2026-11-01
// Change aim: Build a synthetic anisotropic test volume (ellipsoid, sphere, box) with no patient data.
// File: mpr_slicer.cpp
// Function: makeTestVolume
static void makeTestVolume(vtkImageData* vol)
{
    const int nx = 96, ny = 96, nz = 64;
    vol->SetDimensions(nx, ny, nz);
    vol->SetSpacing(1.0, 1.0, 2.0);            // thicker slices in z, like real CT
    vol->SetOrigin(0.0, 0.0, 0.0);
    vol->AllocateScalars(VTK_FLOAT, 1);
    for (int z = 0; z < nz; ++z)
        for (int y = 0; y < ny; ++y)
            for (int x = 0; x < nx; ++x) {
                const double px = x, py = y, pz = z * 2.0;   // physical coordinates in mm
                float v = 0.0f;
                double e = std::pow((px - 48) / 40, 2) + std::pow((py - 48) / 30, 2) + std::pow((pz - 64) / 50, 2);
                if (e < 1.0) v = 100.0f;                                   // body ellipsoid
                double s = std::pow(px - 35, 2) + std::pow(py - 55, 2) + std::pow(pz - 50, 2);
                if (s < 12.0 * 12.0) v = 255.0f;                           // bright sphere
                if (px > 58 && px < 74 && py > 30 && py < 46 && pz > 70 && pz < 100) v = 180.0f;  // box
                vol->SetScalarComponentFromFloat(x, y, z, 0, v);
            }
}

// BEN 2026-11-01
// Change aim: Reslice the volume on one plane and save the result as an 8-bit PNG.
// File: mpr_slicer.cpp
// Function: saveSlice
static void saveSlice(vtkImageData* vol, vtkMatrix4x4* axes, const std::string& name, int size)
{
    double range[2];
    vol->GetScalarRange(range);
    const double minSp = std::min(std::min(vol->GetSpacing()[0], vol->GetSpacing()[1]), vol->GetSpacing()[2]);

    vtkNew<vtkImageReslice> reslice;
    reslice->SetInputData(vol);
    reslice->SetOutputDimensionality(2);
    reslice->SetResliceAxes(axes);
    reslice->SetInterpolationModeToLinear();
    reslice->SetOutputSpacing(minSp, minSp, 1.0);
    reslice->SetOutputOrigin(-0.5 * size * minSp, -0.5 * size * minSp, 0.0);
    reslice->SetOutputExtent(0, size - 1, 0, size - 1, 0, 0);
    reslice->SetBackgroundLevel(range[0]);

    vtkNew<vtkImageShiftScale> toByte;
    toByte->SetInputConnection(reslice->GetOutputPort());
    toByte->SetShift(-range[0]);
    toByte->SetScale(range[1] > range[0] ? 255.0 / (range[1] - range[0]) : 1.0);
    toByte->SetOutputScalarTypeToUnsignedChar();
    toByte->ClampOverflowOn();

    vtkNew<vtkPNGWriter> writer;
    writer->SetFileName(name.c_str());
    writer->SetInputConnection(toByte->GetOutputPort());
    writer->Write();
    std::cout << "saved " << name << std::endl;
}

// BEN 2026-11-01
// Change aim: Build a slice-plane matrix from three axis vectors and the volume centre.
// File: mpr_slicer.cpp
// Function: planeMatrix
static void planeMatrix(vtkMatrix4x4* m, const double x[3], const double y[3], const double z[3], const double c[3])
{
    m->Identity();
    for (int i = 0; i < 3; ++i) {      // columns are the plane axes in volume coordinates
        m->SetElement(i, 0, x[i]);
        m->SetElement(i, 1, y[i]);
        m->SetElement(i, 2, z[i]);
        m->SetElement(i, 3, c[i]);
    }
}

// BEN 2026-11-01
// Change aim: Load a volume (DICOM folder or synthetic), then save the four slice views.
// File: mpr_slicer.cpp
// Function: main
int main(int argc, char** argv)
{
    vtkNew<vtkImageData> synthetic;
    vtkImageData* vol = nullptr;
    vtkNew<vtkDICOMImageReader> reader;

    if (argc > 1) {                                   // argument: folder with a DICOM series
        reader->SetDirectoryName(argv[1]);
        reader->Update();
        vol = reader->GetOutput();
        if (vol->GetNumberOfPoints() == 0) {
            std::cerr << "No DICOM images found in: " << argv[1] << std::endl;
            return 1;
        }
    } else {
        makeTestVolume(synthetic);
        vol = synthetic;
    }

    int dims[3];
    double sp[3], org[3];
    vol->GetDimensions(dims);
    vol->GetSpacing(sp);
    vol->GetOrigin(org);
    double c[3];
    for (int i = 0; i < 3; ++i)
        c[i] = org[i] + 0.5 * sp[i] * (dims[i] - 1);   // centre of the volume in mm
    std::cout << "volume " << dims[0] << "x" << dims[1] << "x" << dims[2]
              << "  spacing " << sp[0] << "," << sp[1] << "," << sp[2]
              << "  centre " << c[0] << "," << c[1] << "," << c[2] << std::endl;

    const double ex[3] = {1, 0, 0}, ey[3] = {0, 1, 0}, ez[3] = {0, 0, 1};
    const double nez[3] = {0, 0, 1}, ney[3] = {0, -1, 0};
    const int size = 160;
    vtkNew<vtkMatrix4x4> m;

    planeMatrix(m, ex, ey, ez, c);                     // axial
    saveSlice(vol, m, "axial.png", size);
    planeMatrix(m, ex, nez, ney, c);                   // coronal: x, z, -y
    saveSlice(vol, m, "coronal.png", size);
    const double sy[3] = {0, 1, 0};
    planeMatrix(m, sy, nez, ex, c);                    // sagittal: y, z, x
    saveSlice(vol, m, "sagittal.png", size);

    // oblique: axial plane tilted 30 deg about x and 20 deg about y
    vtkNew<vtkTransform> t;
    t->RotateX(30.0);
    t->RotateY(20.0);
    vtkMatrix4x4* r = t->GetMatrix();
    double ox[3], oy[3], oz[3];
    for (int i = 0; i < 3; ++i) {
        ox[i] = r->GetElement(i, 0);
        oy[i] = r->GetElement(i, 1);
        oz[i] = r->GetElement(i, 2);
    }
    planeMatrix(m, ox, oy, oz, c);
    saveSlice(vol, m, "oblique.png", size);
    return 0;
}
