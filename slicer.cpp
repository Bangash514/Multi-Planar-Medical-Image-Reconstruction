Multi-planar medical image reconstruction is a complex topic that involves many different algorithms and techniques. While it is possible to create a basic 
demo in C++, the full implementation of a multi-planar medical image reconstruction system would require significant time and resources.That being said, 
here is an example of how to use the ITK library in C++ to perform multi-planar reconstruction:

#include <itkImage.h>
#include <itkImageFileReader.h>
#include <itkExtractImageFilter.h>
#include <itkRescaleIntensityImageFilter.h>
#include <itkImageFileWriter.h>

typedef itk::Image<float, 3> ImageType;

int main(int argc, char* argv[])
{
    if (argc < 3) {
        std::cerr << "Usage: " << std::endl;
        std::cerr << argv[0] << " inputImage outputImage" << std::endl;
        return EXIT_FAILURE;
    }

    // Read the input image
    itk::ImageFileReader<ImageType>::Pointer reader = itk::ImageFileReader<ImageType>::New();
    reader->SetFileName(argv[1]);

    // Extract a slice in the sagittal plane
    itk::ExtractImageFilter<ImageType, ImageType>::Pointer extractor = itk::ExtractImageFilter<ImageType, ImageType>::New();
    ImageType::RegionType sagittalRegion = reader->GetOutput()->GetLargestPossibleRegion();
    sagittalRegion.SetSize(0, 0);
    extractor->SetExtractionRegion(sagittalRegion);
    extractor->SetInput(reader->GetOutput());

    // Rescale the intensity of the image
    itk::RescaleIntensityImageFilter<ImageType, ImageType>::Pointer rescaler = itk::RescaleIntensityImageFilter<ImageType, ImageType>::New();
    rescaler->SetInput(extractor->GetOutput());
    rescaler->SetOutputMinimum(0);
    rescaler->SetOutputMaximum(255);

    // Write the output image
    itk::ImageFileWriter<ImageType>::Pointer writer = itk::ImageFileWriter<ImageType>::New();
    writer->SetFileName(argv[2]);
    writer->SetInput(rescaler->GetOutput());
    writer->Update();

    return EXIT_SUCCESS;
}
