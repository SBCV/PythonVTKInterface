import vtk

from Utility.Logging_Extension import logger
from Utility.Math.Conversion.Conversion_Collection import convert_computer_vision_to_opengl_camera

from VTKInterface.Interfaces.Camera_Extrinsic_Interface import CameraExtrinsicInterface
from VTKInterface.Interfaces.Camera_Intrinsic_Interface import CameraIntrinsicInterface


class CameraInterface(CameraExtrinsicInterface, CameraIntrinsicInterface):

    def __init__(self, vtk_renderer=None, vtk_render_window=None):

        self.init_instance_variable(
            "vtk_renderer", vtk_renderer, vtk.vtkRenderer())
        self.init_instance_variable(
            "vtk_render_window", vtk_render_window, vtk.vtkRenderWindow())

    def get_active_camera(self):
        return self.vtk_renderer.GetActiveCamera()

    def look_with_camera_on_scene(self):
        # https://vtk.org/doc/nightly/html/classvtkRenderer.html#ae8055043e676defbbacff6f1ea65ad1e
        #   Automatically set up the camera based on the visible actors.
        self.vtk_renderer.ResetCamera()

    def set_active_cam_from_computer_vision_cam(self, computer_vision_cam, max_clipping_range=100.0):
        self.set_active_cam_from_computer_vision_cam_to_world_mat(
            computer_vision_cam.get_4x4_cam_to_world_mat(),
            computer_vision_cam.get_calibration_mat(),
            computer_vision_cam.width,
            computer_vision_cam.height,
            max_clipping_range=max_clipping_range)

    def set_active_cam_from_computer_vision_cam_to_world_mat(self,
                                                             cam_to_world_computer_vision_np_mat,
                                                             calibration_np_mat,
                                                             width,
                                                             height,
                                                             max_clipping_range=100.0):
        cam_to_world_opengl_np_mat = convert_computer_vision_to_opengl_camera(
            cam_to_world_computer_vision_np_mat)
        self.set_active_cam_from_opengl_cam_to_world_mat(
            cam_to_world_opengl_np_mat,
            calibration_np_mat,
            width,
            height,
            max_clipping_range=max_clipping_range)

    def set_active_cam_from_opengl_cam(self,
                                       opengl_cam,
                                       max_clipping_range=100.0):

        self.set_active_cam_from_opengl_cam_to_world_mat(
            opengl_cam.get_4x4_cam_to_world_mat(),
            opengl_cam.get_calibration_mat(),
            opengl_cam.width,
            opengl_cam.height,
            max_clipping_range=max_clipping_range)

    def set_active_cam_from_opengl_cam_to_world_mat(self,
                                                    cam_to_world_opengl_np_mat,
                                                    calibration_np_mat,
                                                    width,
                                                    height,
                                                    max_clipping_range=100.0):
        logger.info('set_active_cam_from_opengl_cam_to_world_mat: ...')

        # https://github.com/Kitware/VTK/blob/master/Rendering/Core/vtkCamera.h
        # https://github.com/Kitware/VTK/blob/master/Rendering/Core/vtkCamera.cxx

        # =============================================================
        # ModelViewTransform = ViewTransform * ModelTransform
        # ViewTransform depends only on Position, FocalPoint and ViewUp
        # =============================================================

        self.set_active_cam_intrinsics(
            calibration_np_mat, width, height, max_clipping_range)

        self.set_active_cam_model_view_transformation(
            cam_to_world_opengl_np_mat)

        # IMPORTANT OTHERWISE THE VISUALIZATION IS BUGGY
        self.vtk_renderer.ResetCameraClippingRange()
        # # Always call the render function of the window, not the renderer itself
        # self.vtk_render_window.Render()

        logger.info('set_active_cam_from_opengl_cam_to_world_mat: Done')

    def set_active_cam_from_opengl_cam_legacy(self,
                                              opengl_cam,
                                              max_clipping_range=100.0):

        # The virtual camera MUST be initialized with an OpenGl cam_to_world_mat
        self.set_active_cam_model_view_transformation_from_opengl_cam(
            opengl_cam)
        self.set_active_cam_intrinsics_from_virtual_cam(
            opengl_cam,
            max_clipping_range)

# ========================================= Notes =========================================
# ModelTransformationMatrix
#   https://vtk.org/doc/nightly/html/classvtkCamera.html#a1f0aeb85411e5628c30cb31cbb1aceeb
#       GetModelTransformMatrix()
#       SetModelTransformMatrix (const double elements[16])
#           This matrix could be used for model related transformations such as
#           scale, shear, rotations and translations.

# ModelViewTransformMatrix
#   https://vtk.org/doc/nightly/html/classvtkCamera.html#aaa01944877ddc78628f7f98a4331d78b
#       GetModelViewTransformMatrix ()
#       Return the model view matrix of model view transform.

# ViewTransformMatrix
#   https://vtk.org/doc/nightly/html/classvtkCamera.html#a40f9e41a86e5b7c94fe171e7b9193673
#       GetViewTransformMatrix()
#           For backward compatibility.
#           Use GetModelViewTransformMatrix() now.
#           Return the matrix of the view transform. The ViewTransform depends on only three ivars:
#           the Position, the FocalPoint, and the ViewUp vector.

# GetProjectionTransformMatrix(double aspect, double nearz, double farz)
# CompositeProjectionTransformMatrix
#   https://vtk.org/doc/nightly/html/classvtkCamera.html#acb7e327cd7644e8ae885bac78221bc79
#       GetCompositeProjectionTransformMatrix (double aspect, double nearz, double farz)
#           Return the concatenation of the ViewTransform and the ProjectionTransform.

# ProjectionTransformMatrix()
#   https://vtk.org/doc/nightly/html/classvtkCamera.html#aa3244d44cbbb5c199b69263f97c5af52
#       GetProjectionTransformMatrix()
#           Return the projection transform matrix, which converts from camera coordinates to viewport coordinates.



