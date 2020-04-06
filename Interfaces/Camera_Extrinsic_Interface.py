import vtk
import numpy as np

from VTKInterface.Interfaces.Base_Interface import BaseInterface
from VTKInterface.Utility.Conversion_Utility import convert_numpy_array_to_vtk_transform
from VTKInterface.Utility.Conversion_Utility import convert_vtk_matrix_to_numpy_array


class CameraExtrinsicInterface(BaseInterface):

    def __init__(self, vtk_renderer=None, vtk_render_window=None):

        self.init_instance_variable(
            "vtk_renderer", vtk_renderer, vtk.vtkRenderer())
        self.init_instance_variable(
            "vtk_render_window", vtk_render_window, vtk.vtkRenderWindow())

    def print_active_camera_pose(self):
        active_vtk_camera = self.vtk_renderer.GetActiveCamera()
        print("GetPosition()", active_vtk_camera.GetPosition())
        print("GetViewUp()", active_vtk_camera.GetViewUp())
        print("GetFocalPoint()", active_vtk_camera.GetFocalPoint())

    def set_active_cam_model_view_transformation(self, np_mat):
        self.set_active_cam_model_view_transformation_to_identity()
        active_vtk_camera = self.vtk_renderer.GetActiveCamera()

        vtk_transform = convert_numpy_array_to_vtk_transform(np_mat)
        active_vtk_camera.ApplyTransform(vtk_transform)

    def set_active_cam_model_view_transformation_to_identity(self):
        active_vtk_camera = self.vtk_renderer.GetActiveCamera()

        # By default the VTK camera is shifted by (0, 0, 1), i.e.
        # active_vtk_camera.GetPosition() returns (0.0, 0.0, 1.0)

        # Option 1
        # inverse_transform = vtk.vtkTransform()
        # inverse_transform.Identity()
        # # GetModelViewTransformMatrix() returns a cam_to_world_matrix
        # # Therefore, it is already the inverse of the previous world_to_cam_matrix
        # model_view_mat = active_vtk_camera.GetModelViewTransformMatrix()
        # inverse_transform.Concatenate(model_view_mat)
        # active_vtk_camera.ApplyTransform(inverse_transform)

        # Option 2
        active_vtk_camera.SetFocalPoint(0.0, 0.0, -1.0)
        active_vtk_camera.SetViewUp(0.0, 1.0, 0.0)
        active_vtk_camera.SetPosition(0.0, 0.0, 0.0)

        model_view_trans_mat = convert_vtk_matrix_to_numpy_array(
            active_vtk_camera.GetModelViewTransformMatrix())
        assert np.array_equal(
            model_view_trans_mat,
            np.identity(4, dtype=float))

    def set_active_cam_model_view_transformation_from_opengl_cam(self,
                                                                 opengl_cam):

        # The virtual camera MUST be initialized with an OpenGl cam_to_world_mat

        active_vtk_camera = self.vtk_renderer.GetActiveCamera()
        camera_center = opengl_cam.get_camera_center()
        active_vtk_camera.SetPosition(camera_center)
        viewing_dir = opengl_cam.cam_direction_to_world_direction(
            np.array([0, 0, -1]))
        focal_point = camera_center + viewing_dir
        active_vtk_camera.SetFocalPoint(focal_point)
        # active_vtk_camera.ComputeViewPlaneNormal()
        view_up = opengl_cam.cam_direction_to_world_direction(
            np.array([0, 1, 0]))
        active_vtk_camera.SetViewUp(view_up)
