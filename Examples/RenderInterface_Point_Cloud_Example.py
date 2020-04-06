import vtk
from numpy import random
from VTKInterface.Interfaces.Render_Interface import RenderInterface
from VTKInterface.Utility.Actor_Utility import ActorUtility

num_points = 1000
colors = [[255, 0, 0] for k in range(num_points)]
coords = [20 * (random.rand(3) - 0.5) for k in range(num_points)]
point_cloud_actor = ActorUtility.create_vtk_point_cloud_actor(coords, colors)

render_interface = RenderInterface(
    off_screen_rendering=False,
    width=320,
    height=240,
    background_color=(1.0, 1.0, 1.0))
render_interface.add_actor(point_cloud_actor)
render_interface.look_with_camera_on_scene()
render_interface.render_and_start()


