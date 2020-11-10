import numpy as np
from Utility.Logging_Extension import logger
from matplotlib import pyplot as plt

import vtk
from vtk.util import numpy_support

from VTKInterface.Interfaces.Base_Interface import BaseInterface
from VTKInterface.Utility.Data_Utility import DataUtility

class ZBufferInterface(BaseInterface):

    def __init__(self, vtk_renderer=None, vtk_render_window=None, width=None, height=None):

        """
        Do not confuse z_buffer with depth_buffer!
        * z_buffer contains values in [0,1]
        * depth_buffer contains the actual distance values
        """

        self.init_instance_variable(
            "vtk_renderer", vtk_renderer, vtk.vtkRenderer())
        self.init_instance_variable(
            "vtk_render_window", vtk_render_window, vtk.vtkRenderWindow())

        self.width = width
        self.height = height

    # def get_z_buffer_sparse(self, sparsity=100):
    #     z_buffer_data_numpy = self.get_opengl_z_buffer_as_numpy_arr()
    #     z_buffer_sparse = z_buffer_data_numpy[::sparsity]
    #     return z_buffer_sparse.flatten()

    def get_opengl_z_buffer_as_numpy_arr(self):
        """
        Returns the z buffer values in [0,1] in image coordinates
        The z buffer corresponds to an image starting at the lower left (0,0)
        """
        if not self.vtk_render_window.GetOffScreenRendering():
            error_str = 'THIS ONLY WORKS IN OFF SCREEN MODE ' \
                        '(use off_screen_rendering=True in render_interface constructor)'
            assert False, error_str
        # http://berkgeveci.github.io/page7/
        z_buffer_data = vtk.vtkFloatArray()
        # GetZbufferData (int x, int y, int x2, int y2, vtkFloatArray *z)
        self.vtk_render_window.GetZbufferData(
            0, 0, self.render_width - 1, self.render_height - 1, z_buffer_data)
        z_buffer_data_numpy = numpy_support.vtk_to_numpy(z_buffer_data)
        z_buffer_data_numpy = np.reshape(z_buffer_data_numpy, (-1, self.render_width))
        return z_buffer_data_numpy

    def get_computer_vision_z_buffer_as_numpy_arr(self):
        """ z_buffer contains values in [0,1]  """
        opengl_z_buffer = self.get_opengl_z_buffer_as_numpy_arr()
        # flipping along the first axis (y)
        return np.flipud(opengl_z_buffer)

    def get_z_buffer_as_world_coords(self, n_th_result_point=10):
        """ z_buffer contains values in [0,1]  """
        z_buffer_matrix = self.get_opengl_z_buffer_as_numpy_arr()
        return self.convert_z_buffer_mat_to_world_coords(z_buffer_matrix, n_th_result_point)

    def convert_z_buffer_mat_to_world_coords(self, z_buffer_matrix, n_th_result_point=10):
        """ z_buffer contains values in [0,1]  """

        # https://vtk.org/doc/nightly/html/classvtkDepthImageToPointCloud.html
        # https://github.com/Kitware/VTK/blob/master/Rendering/Image/vtkDepthImageToPointCloud.h
        #   TODO
        #   e.g. vtk.vtkDepthImageToPointCloud() is part of the python interface

        world_coords = []
        index = 0
        num_values = z_buffer_matrix.shape[0] * z_buffer_matrix.shape[1]
        for (y, x), z_value in np.ndenumerate(z_buffer_matrix):
            if index % 10000 == 0:
                logger.info('index: ' + str(index) + ' of ' + str(num_values))
            # We assume that points lying on the clipping plane are not part of the scene
            if z_value < 1.0:
                if index % n_th_result_point == 0:
                    # https://www.vtk.org/doc/nightly/html/classvtkViewport.html
                    self.vtk_renderer.SetDisplayPoint(x, y, z_value)    # TODO REMOVE REDUNDANT?
                    # https://www.vtk.org/doc/nightly/html/classvtkRenderer.html

                    world_coord = self._vtk_convert_display_coord_to_world_coord(x, y, z_value)
                    world_coords.append(world_coord)
            index += 1

        return world_coords

    def _vtk_convert_display_coord_to_world_coord(self, x, y, z):

        self.vtk_renderer.SetDisplayPoint(x, y, z)
        self.vtk_renderer.DisplayToWorld()
        world_coord_hom = self.vtk_renderer.GetWorldPoint()
        world_coord_hom = np.asarray(world_coord_hom, dtype=float)
        world_coord_hom /= world_coord_hom[3]
        world_coord = world_coord_hom[0:3]
        return world_coord

    def get_computer_vision_depth_buffer_as_numpy_arr(self):

        # https://stackoverflow.com/questions/6652253/getting-the-true-z-value-from-the-depth-buffer

        # https://discourse.paraview.org/t/help-how-create-a-depth-map-using-paraview-is-it-possible/738

        # https://stackoverflow.com/questions/17659362/get-depth-from-camera-for-each-pixel
        #   according to the comments here, the depth buffer is not linearly spaced

        z_buffer_data_numpy = self.get_computer_vision_z_buffer_as_numpy_arr()
        z_near, z_far = self.get_clipping_range()
        # logger.vinfo('z_near', z_near)
        # logger.vinfo('z_far', z_far)

        # http://web.archive.org/web/20130416194336/http://olivers.posterous.com/linear-depth-in-glsl-for-real
        #   See the 3rd code block
        numerator = 2.0 * z_near * z_far
        denominator = z_far + z_near - (2.0 * z_buffer_data_numpy - 1.0) * (z_far - z_near)
        depth_buffer_data_numpy = numerator/denominator
        depth_buffer_data_numpy[z_buffer_data_numpy == 1.0] = 0

        return depth_buffer_data_numpy

    def get_clipping_range(self):
        return self.vtk_renderer.GetActiveCamera().GetClippingRange()

    def write_z_buffer_to_disc(self, jpeg_ofp):
        """ z_buffer contains values in [0,1]  """

        # Make sure the opacity of the object is 1

        window_to_image_filter = vtk.vtkWindowToImageFilter()
        image_shift_scale = vtk.vtkImageShiftScale()
        image_writer = vtk.vtkJPEGWriter()

        window_to_image_filter.SetInput(self.vtk_render_window)
        # window_to_image_filter.SetMagnification(1)
        window_to_image_filter.SetInputBufferTypeToZBuffer()

        image_shift_scale.SetOutputScalarTypeToUnsignedChar()
        image_shift_scale.SetInputConnection(window_to_image_filter.GetOutputPort())
        image_shift_scale.SetShift(0)
        image_shift_scale.SetScale(-255)

        image_writer.SetFileName(jpeg_ofp)
        image_writer.SetInputConnection(image_shift_scale.GetOutputPort())
        image_writer.Write()

    def write_z_buffer_visualization_to_disc(self, z_buffer_viz_ofp):
        """ z_buffer contains values in [0,1]  """

        z_buffer_data_numpy = self.get_opengl_z_buffer_as_numpy_arr()
        fig = plt.figure(frameon=False)
        fig.set_size_inches(self.width / 100.0, self.height / 100.0)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.imshow(
            z_buffer_data_numpy,
            aspect='auto',
            origin='lower',
            cmap='gray')
        fig.savefig(z_buffer_viz_ofp)

    def show_z_buffer(self):
        z_buffer_data_numpy = self.get_opengl_z_buffer_as_numpy_arr()
        plt.imshow(
            z_buffer_data_numpy,
            origin='lower',
            cmap='gray')
        plt.axis('off')
        plt.show()

    ########################################################################

    def convert_z_buffer_list_with_none_to_world_coords(self,
                                                        pixel_z_values,
                                                        computer_vision_pixels=True):

        world_coords = []
        for index, vec in enumerate(pixel_z_values):
            if vec is None:
                world_coords.append(None)
            else:
                (x, y, z_value) = vec
                # We assume that points lying on the clipping plane are not part of the scene
                if z_value < 1.0:
                    # does not work
                    if computer_vision_pixels:      # rotation around the x axis
                        y = self.render_height - y
                    world_coord = self._vtk_convert_display_coord_to_world_coord(x, y, z_value)
                    world_coords.append(world_coord)
                else:
                    world_coords.append(None)
        return world_coords