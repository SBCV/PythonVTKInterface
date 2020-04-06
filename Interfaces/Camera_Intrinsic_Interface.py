import vtk

from Utility.Types.Camera import Camera
from VTKInterface.Interfaces.Base_Interface import BaseInterface


class CameraIntrinsicInterface(BaseInterface):

    def __init__(self, vtk_renderer=None, vtk_render_window=None):

        self.init_instance_variable(
            "vtk_renderer", vtk_renderer, vtk.vtkRenderer())
        self.init_instance_variable(
            "vtk_render_window", vtk_render_window, vtk.vtkRenderWindow())

    def set_principal_point(self, principal_pt, width, height):
        vtk_camera = self.vtk_renderer.GetActiveCamera()
        # https://gist.github.com/decrispell/fc4b69f6bedf07a3425b
        # // convert the principal point to window center (normalized coordinate system) and set it
        wcx = -2 * (principal_pt[0] - width / 2.0) / float(width)
        wcy = 2 * (principal_pt[1] - height / 2.0) / float(height)
        vtk_camera.SetWindowCenter(wcx, wcy)

    def set_active_cam_intrinsics(self, np_mat, width, height, max_clipping_range=100.0):
        active_vtk_camera = self.vtk_renderer.GetActiveCamera()
        focal_length = np_mat[0][0]
        view_angle = Camera.compute_view_angle(
            focal_length, width, height)
        active_vtk_camera.SetViewAngle(view_angle)
        active_vtk_camera.SetClippingRange(0.0, max_clipping_range)

    def set_active_cam_intrinsics_from_virtual_cam(self,
                                                   virtual_cam,
                                                   max_clipping_range=100.0):
        active_vtk_camera = self.vtk_renderer.GetActiveCamera()
        view_angle = virtual_cam.get_view_angle()
        active_vtk_camera.SetViewAngle(view_angle)
        active_vtk_camera.SetClippingRange(0.0, max_clipping_range)
