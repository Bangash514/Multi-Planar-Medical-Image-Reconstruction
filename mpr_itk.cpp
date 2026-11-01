// BEN 2026-11-01
// Change aim: Extract axial, coronal and sagittal slices from a 3D volume with ITK 5.
// File: mpr_itk.cpp
#include "itkImage.h"
#include "itkImageRegionIteratorWithIndex.h"
#include "itkImageFileWriter.h"
#include "itkImageSeriesReader.h"
#include "itkGDCMImageIO.h"
#include "itkGDCMSeriesFileNames.h"
#include "itkExtractImageFilter.h"
#include "itkResampleImageFilter.h"
#include "itkLinearInterpolateImageFunction.h"
#include "itkFlipImageFilter.h"
#include "itkIntensityWindowingImageFilter.h"
#include "itkMinimumMaximumImageCalculator.h"
#include "itkCastImageFilter.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>

typedef itk::Image<float, 3> Image3D;
typedef itk::Image<float, 2> Image2D;
typedef itk::Image<unsigned char, 2> ByteImage2D;

// BEN 2026-11-01
// Change aim: Build a synthetic anisotropic test volume (ellipsoid, sphere, box) with no patient data.
// File: mpr_itk.cpp
// Function: makeTestVolume
static Image3D::Pointer makeTestVolume()
{
    Image3D::Pointer vol = Image3D::New();
    Image3D::SizeType size = {{96, 96, 64}};
    Image3D::SpacingType spacing;
    spacing[0] = 1.0; spacing[1] = 1.0; spacing[2] = 2.0;   // thicker slices in z, like real CT
    Image3D::RegionType region;
    region.SetSize(size);
    vol->SetRegions(region);
    vol->SetSpacing(spacing);
    vol->Allocate();
    vol->FillBuffer(0.0f);

    itk::ImageRegionIteratorWithIndex<Image3D> it(vol, region);
    for (it.GoToBegin(); !it.IsAtEnd(); ++it) {
        const Image3D::IndexType i = it.GetIndex();
        const double px = i[0], py = i[1], pz = i[2] * 2.0;   // physical coordinates in mm
        float v = 0.0f;
        const double e = std::pow((px - 48) / 40, 2) + std::pow((py - 48) / 30, 2) + std::pow((pz - 64) / 50, 2);
        if (e < 1.0) v = 100.0f;
        const double s = std::pow(px - 35, 2) + std::pow(py - 55, 2) + std::pow(pz - 50, 2);
        if (s < 144.0) v = 255.0f;
        if (px > 58 && px < 74 && py > 30 && py < 46 && pz > 70 && pz < 100) v = 180.0f;
        it.Set(v);
    }
    return vol;
}

// BEN 2026-11-01
// Change aim: Read a DICOM series from a folder into a 3D float volume.
// File: mpr_itk.cpp
// Function: readDicom
static Image3D::Pointer readDicom(const std::string& dir)
{
    typedef itk::GDCMSeriesFileNames Names;
    Names::Pointer names = Names::New();
    names->SetUseSeriesDetails(true);
    names->SetDirectory(dir);
    const std::vector<std::string>& files = names->GetInputFileNames();
    if (files.empty()) return nullptr;

    typedef itk::ImageSeriesReader<Image3D> Reader;
    Reader::Pointer reader = Reader::New();
    reader->SetImageIO(itk::GDCMImageIO::New());
    reader->SetFileNames(files);
    reader->Update();
    return reader->GetOutput();
}

// BEN 2026-11-01
// Change aim: Extract one slice, make pixels square, scale to 8 bit and save as PNG.
// File: mpr_itk.cpp
// Function: saveSlice
// axis: 0 sagittal (x fixed), 1 coronal (y fixed), 2 axial (z fixed)
static void saveSlice(Image3D* vol, unsigned int axis, const std::string& name, float lo, float hi)
{
    Image3D::RegionType full = vol->GetLargestPossibleRegion();
    Image3D::SizeType size = full.GetSize();
    Image3D::IndexType start = full.GetIndex();
    start[axis] += size[axis] / 2;          // middle slice
    size[axis] = 0;                         // collapse this axis
    Image3D::RegionType sliceRegion;
    sliceRegion.SetIndex(start);
    sliceRegion.SetSize(size);

    typedef itk::ExtractImageFilter<Image3D, Image2D> Extract;
    Extract::Pointer extract = Extract::New();
    extract->SetInput(vol);
    extract->SetExtractionRegion(sliceRegion);
    extract->SetDirectionCollapseToIdentity();
    extract->Update();
    Image2D::Pointer slice = extract->GetOutput();

    // resample to square pixels (min spacing) so thick slices are not squashed
    Image2D::SpacingType sp = slice->GetSpacing();
    Image2D::SizeType sz = slice->GetLargestPossibleRegion().GetSize();
    const double minSp = std::min(sp[0], sp[1]);
    Image2D::SpacingType newSp;
    newSp.Fill(minSp);
    Image2D::SizeType newSz;
    newSz[0] = static_cast<itk::SizeValueType>(std::lround(sz[0] * sp[0] / minSp));
    newSz[1] = static_cast<itk::SizeValueType>(std::lround(sz[1] * sp[1] / minSp));

    typedef itk::ResampleImageFilter<Image2D, Image2D> Resample;
    Resample::Pointer resample = Resample::New();
    resample->SetInput(slice);
    resample->SetOutputSpacing(newSp);
    resample->SetSize(newSz);
    resample->SetOutputOrigin(slice->GetOrigin());
    resample->SetOutputDirection(slice->GetDirection());
    resample->SetInterpolator(itk::LinearInterpolateImageFunction<Image2D, double>::New());
    resample->SetDefaultPixelValue(0.0f);

    // coronal and sagittal: flip so that z points up in the picture
    typedef itk::FlipImageFilter<Image2D> Flip;
    Flip::Pointer flip = Flip::New();
    Flip::FlipAxesArrayType axes;
    axes[0] = false;
    axes[1] = (axis != 2);
    flip->SetFlipAxes(axes);
    flip->SetInput(resample->GetOutput());

    // scale with the range of the whole volume (lo, hi), so all views share the same grey levels
    typedef itk::IntensityWindowingImageFilter<Image2D, Image2D> Window;
    Window::Pointer rescale = Window::New();
    rescale->SetInput(flip->GetOutput());
    rescale->SetWindowMinimum(lo);
    rescale->SetWindowMaximum(hi);
    rescale->SetOutputMinimum(0);
    rescale->SetOutputMaximum(255);

    typedef itk::CastImageFilter<Image2D, ByteImage2D> Cast;
    Cast::Pointer cast = Cast::New();
    cast->SetInput(rescale->GetOutput());

    typedef itk::ImageFileWriter<ByteImage2D> Writer;
    Writer::Pointer writer = Writer::New();
    writer->SetFileName(name);
    writer->SetInput(cast->GetOutput());
    writer->Update();
    std::cout << "saved " << name << std::endl;
}

// BEN 2026-11-01
// Change aim: Load a volume (DICOM folder or synthetic), then save the three slice views.
// File: mpr_itk.cpp
// Function: main
int main(int argc, char** argv)
{
    Image3D::Pointer vol;
    if (argc > 1) {                                   // argument: folder with a DICOM series
        vol = readDicom(argv[1]);
        if (vol.IsNull()) {
            std::cerr << "No DICOM series found in: " << argv[1] << std::endl;
            return 1;
        }
    } else {
        vol = makeTestVolume();
    }

    Image3D::SizeType s = vol->GetLargestPossibleRegion().GetSize();
    Image3D::SpacingType sp = vol->GetSpacing();
    std::cout << "volume " << s[0] << "x" << s[1] << "x" << s[2]
              << "  spacing " << sp[0] << "," << sp[1] << "," << sp[2] << std::endl;

    // grey range of the whole volume, computed before any slice is extracted
    vol->SetRequestedRegionToLargestPossibleRegion();
    typedef itk::MinimumMaximumImageCalculator<Image3D> MinMax;
    MinMax::Pointer mm = MinMax::New();
    mm->SetImage(vol);
    mm->Compute();
    const float lo = mm->GetMinimum(), hi = mm->GetMaximum();

    saveSlice(vol, 2, "itk_axial.png", lo, hi);
    saveSlice(vol, 1, "itk_coronal.png", lo, hi);
    saveSlice(vol, 0, "itk_sagittal.png", lo, hi);
    return 0;
}
