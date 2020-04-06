import vtk

# create a Sphere
sphereSource = vtk.vtkSphereSource()
sphereSource.SetCenter(0.0, 0.0, 0.0)
sphereSource.SetRadius(0.5)
sphereMapper = vtk.vtkPolyDataMapper()
sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
sphereActor = vtk.vtkActor()
sphereActor.SetMapper(sphereMapper)

# a renderer and render window
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# add the actors to the scene
renderer.AddActor(sphereActor)
renderer.SetBackground(.1, .2, .3)  # Background dark blue

transform = vtk.vtkTransform()

axes = vtk.vtkAxesActor()
#  The axes are positioned with a user transform
axes.SetUserTransform(transform)

renderer.AddActor(axes)

# Reset camera, i.e. look with camera on existing actors
renderer.ResetCamera()
renderWindow.Render()

# begin mouse interaction
renderWindowInteractor.Start()