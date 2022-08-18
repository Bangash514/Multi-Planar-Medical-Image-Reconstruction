''''''
#Medical Multi-Planar Image Reconstrcution
#November 2021
''''''

import vtk
import numpy as np
from vtk.util.misc import vtkGetDataRoot
#from utils import read_CT_image

# numpyImage, numpyOrigin, numpySpacing = read_CT_image(r"E:\Data\Annotation\3Dircadb1\3Dircadb1.3\PATIENT_DICOM\PATIENT_DICOM")
# print(numpyImage.shape)
# print(numpyOrigin)
# print(numpySpacing)

reader = vtk.vtkDICOMImageReader()
#reader.SetDirectoryName(r".\ti_mo1")
reader.SetDirectoryName(D:\\Bangash Owais\\timo\\IMG-0001-00001.dcm)
reader.Update()
image_data = reader.GetOutput()
print(image_data.GetSpacing())
print(image_data.GetOrigin())

#Calculate the Center of the Volume
(xMin, xMax, yMin, yMax, zMin, zMax) = image_data.GetExtent()
print((xMin, xMax, yMin, yMax, zMin, zMax))
(xSpacing, ySpacing, zSpacing) = image_data.GetSpacing()
print((xSpacing, ySpacing, zSpacing))
(x0, y0, z0) = image_data.GetOrigin()
print((x0, y0, z0))
(minG, maxG) = image_data.GetScalarRange()
print((minG, maxG))

target_point = np.array([114.10982137, 110.70818668, 171.18514388])
#source_point = np.array([217.75727221, -131.99691163, 28.52666644])
#source_point = np.array([185.15, -99.98, -1130.30])
source_point = np.array([67.89, -149.14, -1089.45])

center = np.array([target_point[0],
                   (yMax + 1) * ySpacing - target_point[1],
                   (zMax + 1) * zSpacing - target_point[2]])
# center = [x0 + xSpacing * 0.5 * (xMin + xMax),
#           y0 + ySpacing * 0.5 * (yMin + yMax),
#           z0 + zSpacing * 0.5 * (zMin + zMax)]
 
# slice matrix
# 4x4矩阵的前三行声明新的坐标系：第一、二、三列分别表示X，Y，Z轴的方向向量，第四列表示坐标系源点 The first three rows 
#..of the 4x4 matrix declare the new coordinate system: the first, second, and third columns represent the
#...direction vectors of the X, Y, and Z axes respectively, and the fourth column represents the source points of the coordinate system.  
# 以target_point到source_point射线为新坐标系的Z轴 Z-axis of the new coordinate system with target_point to source_point rays  
new_z = (target_point - source_point) / np.sqrt(np.sum((target_point - source_point) ** 2))
# new_x = np.array([0, new_z[2], -new_z[1]])  # 右下 low right
# new_x = np.array([new_z[1], -new_z[0], 0])  # 左下 left bottom
new_x = np.array([-new_z[2], 0, new_z[0]])  # 左下
assert np.sum(new_x**2) != 0
new_x = new_x / np.sqrt(np.sum(new_x ** 2))
new_y = np.cross(new_x, new_z)
new_y = new_y / np.sqrt(np.sum(new_y**2))
print((new_x,new_y,new_z))

oblique = vtk.vtkMatrix4x4()
# 横切面 cross-section
# oblique.DeepCopy((1, 0, 0, center[0],
#                   0, 1, 0, center[1],
#                   0, 0, 1, center[2],
#                   0, 0, 0, 1))

# 冠状面 coronal plane
# oblique.DeepCopy((1, 0, 0, center[0],
#                   0, 0, 1, center[1],
#                   0, -1, 0, center[2],
#                   0, 0, 0, 1))

# 矢状面 vertical plane
# oblique.DeepCopy((0, 0, 1, center[0],
#                   -1, 0, 0, center[1],
#                   0, -1, 0, center[2],
#                   0, 0, 0, 1))

oblique.DeepCopy((new_x[0], new_y[0], new_z[0], center[0],
                  new_x[1], new_y[1], new_z[1], center[1],
                  new_x[2], new_y[2], new_z[2], center[2],
                  0, 0, 0, 1))

# Extract a slice in the desired orientation
reslice = vtk.vtkImageReslice()
reslice.SetInputConnection(reader.GetOutputPort())
reslice.SetOutputDimensionality(2)
reslice.SetResliceAxes(oblique)
reslice.SetInterpolationModeToCubic()

# Create a greyscale lookup table
table = vtk.vtkLookupTable()
#table.SetRange(-140, 220)  # image intensity range
table.SetRange(0, 2000)  # image intensity range
table.SetValueRange(0.0, 1.0)  # from black to white
table.SetSaturationRange(0.0, 0.0)  # no color saturation
# table.SetNumberOfColors(256)
# table.SetTableValue(0, 1.0, 0.0, 0.0, 1.0)
# for i in range(1, 256):
#     table.SetTableValue(i, i/255.0, i/255.0, i/255.0, 1.0)
table.SetRampToLinear()
table.Build()

# Map the image through the lookup table
color = vtk.vtkImageMapToColors()
color.SetLookupTable(table)
color.SetInputConnection(reslice.GetOutputPort())

# Display the image
# actor = vtk.vtkImageActor()
# actor.GetMapper().SetInputConnection(color.GetOutputPort())

reslice.Update()
print(type(reslice.GetOutput()))
slice_image = reslice.GetOutput()
print(slice_image.GetExtent())
slice_extent = slice_image.GetExtent()

# Display the intervention line
drawing = vtk.vtkImageCanvasSource2D()
drawing.SetNumberOfScalarComponents(3)
drawing.SetScalarTypeToUnsignedChar()
drawing.SetExtent(slice_extent)
drawing.SetDrawColor(1.0, 1.0, .0)
drawing.FillBox(slice_extent[0], slice_extent[1],
                slice_extent[2], slice_extent[3])
drawing.SetDrawColor(1.0, 0.0, 0.0)
drawing.DrawCircle(int(center[0]), int(center[1]), 5)

# display
blend = vtk.vtkImageBlend()
blend.AddInputConnection(color.GetOutputPort())
blend.AddInputConnection(drawing.GetOutputPort())
blend.SetOpacity(0, .6)
blend.SetOpacity(1, .4)

actor = vtk.vtkImageActor()
actor.GetMapper().SetInputConnection(blend.GetOutputPort())
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
# renderer.AddActor(line_actor)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)

# Set up the interaction
interactorStyle = vtk.vtkInteractorStyleImage()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(interactorStyle)
window.SetInteractor(interactor)
window.Render()

# interactorStyle = vtk.vtkInteractorStyleImage()
# renderWindowInteractor = vtk.vtkRenderWindowInteractor()
# renderWindowInteractor.SetInteractorStyle(interactorStyle)
#
# imageViewer = vtk.vtkImageViewer2()
# imageViewer.SetInputConnection(blend.GetOutputPort())
# imageViewer.SetSize(640, 512)
# imageViewer.SetupInteractor(renderWindowInteractor)
# imageViewer.GetRenderer().ResetCamera()

# Create callbacks for slicing the image
actions = {}
actions["Slicing"] = 0


def ButtonCallback(obj, event):
    if event == "RightButtonPressEvent":
        actions["Slicing"] = 2
    elif event == "LeftButtonPressEvent":
        actions["Slicing"] = 1
    else:
        actions["Slicing"] = 0


def MouseMoveCallback(obj, event):
    global center
    (lastX, lastY) = interactor.GetLastEventPosition()
    (mouseX, mouseY) = interactor.GetEventPosition()
    if actions["Slicing"] == 2:   # 漫游 roam/wander
        deltaY = mouseY - lastY
        reslice.Update()
        sliceSpacing = reslice.GetOutput().GetSpacing()[2]
        matrix = reslice.GetResliceAxes()
        # move the center point that we are slicing through
        # center = matrix.MultiplyPoint((0, 0, sliceSpacing * deltaY, 1))
        center += (sliceSpacing * deltaY) * new_z
        matrix.SetElement(0, 3, center[0])
        matrix.SetElement(1, 3, center[1])
        matrix.SetElement(2, 3, center[2])
        window.Render()
    elif actions["Slicing"] == 1:  # 调节窗宽窗位 Adjust window width and window position.
        deltaY = mouseY - lastY
        deltaX = mouseX - lastX
        table.Build()
        (cur_min_gray, cur_max_gray) = table.GetRange()
        cur_window_width = cur_max_gray - cur_min_gray
        cur_window_level = (cur_max_gray + cur_min_gray) / 2

        new_window_width = cur_window_width + deltaX * 10
        new_window_level = cur_window_level + deltaY * 10
        if new_window_level + new_window_width / 2 > maxG or \
                new_window_level - new_window_width / 2 < minG or new_window_width <= 0:
            new_window_width = cur_window_width
            new_window_level = cur_window_level

        table.SetRange(new_window_level - new_window_width / 2, new_window_level + new_window_width / 2)
        window.Render()
    else:
        interactorStyle.OnMouseMove()


interactorStyle.AddObserver("MouseMoveEvent", MouseMoveCallback)
interactorStyle.AddObserver("RightButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("RightButtonReleaseEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)

# Start interaction
interactor.Start()
