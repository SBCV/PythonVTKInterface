
from VTKInterface.Interfaces.Render_Interface import RenderInterface
from VTKInterface.Utility.Actor_Utility import ActorUtility

render_interface = RenderInterface(
    off_screen_rendering=False,             # Toggle Visualization
    width=1920,
    height=1080)

render_interface.vtk_add_point(
    p=[1, 1, 1],
    color=[0.0, 1.0, 0.0])

mesh_actor = ActorUtility.create_vtk_example_mesh_actor()
render_interface.add_actor(mesh_actor)
render_interface.look_with_camera_on_scene()
render_interface.render_and_start()



