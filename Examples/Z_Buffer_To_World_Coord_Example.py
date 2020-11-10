import os
import numpy as np

from Utility.Logging_Extension import logger
from Utility.Types.Point import Point
from Utility.File_Handler.Colmap_File_Handler import ColmapFileHandler
from VTKInterface.Interfaces.Render_Interface import RenderInterface

parent_dp = os.path.dirname(os.path.realpath(__file__))
poly_ifp = os.path.join(parent_dp, 'Data', 'virtual', 'mesh.obj')
texture_ifp = os.path.join(parent_dp, 'Data', 'virtual', 'texture.jpg')
colmap_model_idp = os.path.join(parent_dp, 'Data', 'virtual', 'colmap_model')


colmap_result_model_odp = os.path.join(parent_dp, 'Data', 'virtual', 'colmap_result_model')
z_buffer_ofp = os.path.join(parent_dp, 'Data', 'virtual', 'z_buffer.jpg')
z_buffer_viz_ofp = os.path.join(parent_dp, 'Data', 'virtual', 'z_buffer_viz.jpg')

cameras, points3D = ColmapFileHandler.parse_colmap_model_folder(
    colmap_model_idp,
    image_dp="")
cam = cameras[0]

width = cam.width
height = cam.height

render_interface = RenderInterface(
    off_screen_rendering=False,
    width=width,
    height=height,
    background_color=(0, 127, 127))

max_clipping_range = 100.0
render_interface.load_vtk_mesh_or_point_cloud(poly_ifp, texture_ifp)

calibration_np_mat = cam.get_calibration_mat()
cam_to_world_mat_computer_vision = cam.get_4x4_cam_to_world_mat()
render_interface.set_active_cam_from_computer_vision_cam_to_world_mat(
    cam_to_world_mat_computer_vision,
    calibration_np_mat,
    cam.width,
    cam.height,
    max_clipping_range=max_clipping_range)

principal_pt = [calibration_np_mat[0][2], calibration_np_mat[1][2]]
logger.vinfo('principal_pt', principal_pt)
render_interface.set_principal_point(
    principal_pt,
    width,
    height)

render_interface.render()

render_interface.write_z_buffer_to_disc(z_buffer_ofp)
render_interface.write_z_buffer_visualization_to_disc(z_buffer_viz_ofp)

world_coords_valid = render_interface.get_z_buffer_as_world_coords(n_th_result_point=1)
points_world_coord = Point.get_points_from_coords(world_coords_valid)
ColmapFileHandler.write_colmap_model(
    odp=colmap_result_model_odp,
    cameras=[cam],
    points=points_world_coord)

render_interface.add_point_cloud(world_coords_valid)
render_interface.render_and_start()