import vtk
import numpy as np
from vtk.util import numpy_support
import matplotlib.pyplot as plt

vtk_renderer = vtk.vtkRenderer()
vtk_render_window = vtk.vtkRenderWindow()
vtk_render_window.AddRenderer(vtk_renderer)
vtk_render_window_interactor = vtk.vtkRenderWindowInteractor()
vtk_render_window_interactor.SetRenderWindow(vtk_render_window)
vtk_render_window_interactor.Initialize()

source = vtk.vtkCubeSource()
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(source.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.RotateX(60.0)
actor.RotateY(-35.0)
vtk_renderer.AddActor(actor)

vtk_render_window.Render()
active_vtk_camera = vtk_renderer.GetActiveCamera()
z_near, z_far = active_vtk_camera.GetClippingRange()

z_buffer_data = vtk.vtkFloatArray()
width, height = vtk_render_window.GetSize()
vtk_render_window.GetZbufferData(
    0, 0, width - 1, height - 1, z_buffer_data)
z_buffer_data_numpy = numpy_support.vtk_to_numpy(z_buffer_data)
z_buffer_data_numpy = np.reshape(z_buffer_data_numpy, (-1, width))
z_buffer_data_numpy = np.flipud(z_buffer_data_numpy)  # flipping along the first axis (y)


numerator = 2.0 * z_near * z_far
denominator = z_far + z_near - (2.0 * z_buffer_data_numpy - 1.0) * (z_far - z_near)
depth_buffer_data_numpy = numerator / denominator
non_depth_data_value = np.nan
depth_buffer_data_numpy[z_buffer_data_numpy == 1.0] = non_depth_data_value


print(np.nanmin(depth_buffer_data_numpy))
print(np.nanmax(depth_buffer_data_numpy))

plt.imshow(np.asarray(depth_buffer_data_numpy))
plt.show()
