# Medical Image Registration: Sub-pixel Method (C++, OpenCV)

Sub-pixel image registration in C++ with OpenCV. The program shifts an image by a **known** sub-pixel amount, recovers the shift with **phase correlation** (`cv::phaseCorrelate` with a Hanning window), and registers the image back.

## Result (built-in test image, OpenCV 4.6)
| | x (px) | y (px) |
|---|---|---|
| True shift | 3.370 | -2.810 |
| Estimated | 3.561 | -2.879 |
| Error | 0.191 | 0.069 |

Mean absolute difference after registration: 0.006 (image values 0 to 1). Output: `subpixel_result.png` (original | shifted | corrected).

The error is below one pixel, but not exact: phase correlation depends on image texture, and the result here comes from one synthetic image.

## Build and run
```
mkdir build && cd build
cmake .. && make
./subpixel_registration              # synthetic test image
./subpixel_registration my_image.png # your own grayscale image
```
Requires OpenCV 4 and CMake.

## Files
- `subpixel_registration.cpp` - the program
- `CMakeLists.txt` - build file
- `sub-pixel_ImageRegistration.py` - older Python script (uses a scikit-image function that was removed in newer versions)

## Use and contact
If you use, adapt or contribute to this work, please credit the author and **contact or inform me by email: owaiskhan_bangash@yahoo.com**

## Author
BEN, Software Engineer. GitHub: [Bangash514](https://github.com/Bangash514)
