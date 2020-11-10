
from Utility.File_Handler.Colmap_File_Handler import ColmapFileHandler
from VTKInterface.Interfaces.Render_Interface import RenderInterface

import os

parent_dp = os.path.dirname(os.path.realpath(__file__))
poly_ifp = os.path.join(parent_dp, 'Data', 'virtual', 'mesh.obj')
texture_ifp = os.path.join(parent_dp, 'Data', 'virtual', 'texture.jpg')
colmap_model_idp = os.path.join(parent_dp, 'Data', 'virtual', 'colmap_model')

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

render_interface.load_vtk_mesh_or_point_cloud(
    poly_ifp, texture_ifp)

for cam in cameras:
    print(cam.file_name)

    cam_to_world_mat_computer_vision = cam.get_4x4_cam_to_world_mat()
    print("cam_to_world_mat_computer_vision\n", cam_to_world_mat_computer_vision)

    render_interface.add_coordinate_axes_custom(
        cam_to_world_mat_computer_vision,
        length=0.5,
        line_width=2.5,
        add_center=False)

    calibration_np_mat = cam.get_calibration_mat()

    render_interface.set_active_cam_from_computer_vision_cam_to_world_mat(
        cam_to_world_mat_computer_vision,
        calibration_np_mat,
        cam.width,
        cam.height,
        max_clipping_range=1000.0)

render_interface.render_and_start()

