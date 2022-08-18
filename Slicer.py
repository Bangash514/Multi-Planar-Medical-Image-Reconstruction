#Created by Bangash Owais

import vtk
import math
import numpy
import slicer_read_Dataset
from vtk.util.misc import vtkGetDataRoot
VTK_DATA_ROOT = vtkGetDataRoot()

DEBUG_MODE = 0

#-----Initalization ----------

worldPicker = vtk.vtkWorldPointPicker()
clickPointsList = []
renderer = vtk.vtkRenderer()
aslice = range(10)
color = range(10)
actor = range(10)
mpv_renderer = range(4)

#Start by loading some data.
reader = vtk.vtkDICOMImageReader()
reader.SetFileName("D:\\Bangash Owais\\timo\\IMG-0001-00001.dcm")
reader.SetDataExtent(0,63,0,63,1,93)
reader.SetDataSpacing(1,1,1)
#reader.SetDataSpacing(3.2,3.2,1.5)
reader.SetDataOrigin(0.0,0.0,0.0)
reader.SetDataScalarTypeToUnsignedShort()
reader.UpdateWholeExtent()

#Calculate the center of the volume
reader.GetOutput().UpdateInformation()
(xMin,Xmax,yMin,yMax,zMin,zMax) = reader.GetOutput().GetWholeExtent()
(xSpacing, ySpacing, zSpacing) = reader.GetOutput().GetSpacing()
(x0, y0, z0) = reader.GetOutput().GetOrigin()

center = [x0 + xSpacing * 0.5 * (xMin + xMax),
          y0 + ySpacing * 0.5 * (yMin + yMax),
          z0 + zSpacing * 0.5 * (xMin + zMax)]

if DEBUG_MODE:
    print ("(center: )", center)
    print ("(xMin, xMax, yMin, yMax, zMin, zMax)", xMin, xMax, yMin, yMax, zMin, zMax)          

#--------------Basic Planes -----------------------

axial = vtk.vtkMatrix4x4()
axial.DeepCopy((1,0,0, center[0],
                0,1,0, center[1],
                0,0,1, center[2],
                0,0,0,1))

coronal = vtk.vtkMatrix4x4() #x axis
coronalDeepCopy((1,0,0, center[0],
                 0,0,1, center[1],
                 0,-1,1, center[2],
                 0,0,0,1))

sagittal = vtk.vtkMatrix4x4()
sagittal.DeepCopy((0,0,-1, center[0],
                   0,1,0, center[1],
                   0,0,1, center[2],
                   0,0,0,1))

#Oblique slice
obliqueSlice = vtk.vtkImageReslice()
obliqueSlice.SetInoutConnection(reader.GetOutputPort())
obliqueSlice.SetOutputDimensionality(2)
