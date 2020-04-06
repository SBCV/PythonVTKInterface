import numpy as np
from Utility.Logging_Extension import logger
from matplotlib import pyplot as plt

import vtk
from vtk.util import numpy_support

from VTKInterface.Interfaces.Base_Interface import BaseInterface


class ZBufferInterface(BaseInterface):

    def __init__(self, vtk_renderer=None, vtk_render_window=None, width=None, height=None):

        self.init_instance_variable(
            "vtk_renderer", vtk_renderer, vtk.vtkRenderer())
        self.init_instance_variable(
            "vtk_render_window", vtk_render_window, vtk.vtkRenderWindow())

        self.width = width
        self.height = height

    def get_z_buffer_sparse(self, sparsity=100):
        z_buffer_data_numpy = self.get_opengl_z_buffer_as_numpy_arr()
        z_buffer_sparse = z_buffer_data_numpy[::sparsity]
        return z_buffer_sparse.flatten()

    def get_z_buffer_as_numpy_arr_legazy(self):

        # C++ Code
        # https://www.vtk.org/Wiki/VTK/Examples/Cxx/Utilities/ZBuffer#Please_try_the_new_VTKExamples_website.

        # https://www.vtk.org/doc/nightly/html/classvtkRenderWindow.html
        # GetZbufferDataAtPoint()
        # https://www.vtk.org/doc/nightly/html/classvtkRenderWindow.html#a5b2da90b3b396c3fcf816b64a83749eb


        # ================== Access the z data ====================
        # Given a pixel location, return the Z value. The z value is normalized (0,1)
        # between the front and back clipping planes.
        # vtk_renderer.GetZ(x,y)

        # vtk_renderWindow.GetZbufferDataAtPoint(x, y)
        # vtk_renderWindow.GetZbufferData(0, 0, width, height)
        # =======================================================

        width, height = self.vtk_render_window.GetSize()
        z_buffer_data_numpy = np.zeros((height, width), dtype=float)
        pixel_index = 0
        pixel_overall = width * height
        for x in range(0, width):
            for y in range(0, height):
                if pixel_index % 1000 == 0:
                    logger.info(str(pixel_index) + ' of ' + str(pixel_overall))
                z_buffer_data_point = self.vtk_render_window.GetZbufferDataAtPoint(x, y)
                # if z_buffer_data_point != 1.0:
                #     print(z_buffer_data_point)
                z_buffer_data_numpy[y][x] = z_buffer_data_point
                pixel_index += 1
        return z_buffer_data_numpy

    def get_computer_vision_z_buffer_as_numpy_arr(self):

        """
        Returns the z buffer values in image coordinates
        :return:
        """

        opengl_z_buffer = self.get_opengl_z_buffer_as_numpy_arr()
        return np.flipud(opengl_z_buffer)   # flipping along the first axis (y)

    def get_opengl_z_buffer_as_numpy_arr(self):
        """
        Returns the z buffer values in image coordinates
        This z buffer corresponds to an image starting at the lower left (0,0)
        :return:
        """

        # http://berkgeveci.github.io/page7/
        z_buffer_data = vtk.vtkFloatArray()
        # GetZbufferData (int x, int y, int x2, int y2, vtkFloatArray *z)
        self.vtk_render_window.GetZbufferData(
            0, 0, self.render_width - 1, self.render_height - 1, z_buffer_data)
        z_buffer_data_numpy = numpy_support.vtk_to_numpy(z_buffer_data)
        z_buffer_data_numpy = np.reshape(z_buffer_data_numpy, (-1, self.render_width))
        return z_buffer_data_numpy

    def show_z_buffer(self):

        z_buffer_data_numpy = self.get_opengl_z_buffer_as_numpy_arr()
        plt.imshow(z_buffer_data_numpy, origin='lower', cmap='gray')
        plt.axis('off')
        plt.show()

    def convert_z_buffer_to_world_coords(self, z_buffer_matrix, n_th_result_point=10):

        """
        Do not confuse z_buffer with depth_buffer!
        z_buffer contains values in [0,1]
        depth_buffer contains the actual distance values
        :param z_buffer_matrix: contains values between 0 and 1.0
        :return:
        """
        world_coords = []
        index = 0
        num_values = z_buffer_matrix.shape[0] * z_buffer_matrix.shape[1]
        for (y, x), z_value in np.ndenumerate(z_buffer_matrix):
            if index % 1000 == 0:
                logger.info('index: ' + str(index) + ' of ' + str(num_values))
            # We assume that points lying on the clipping plane are not part of the scene
            if z_value < 1.0:
                if index % n_th_result_point == 0:
                    # https://www.vtk.org/doc/nightly/html/classvtkViewport.html
                    self.vtk_renderer.SetDisplayPoint(x, y, z_value)
                    # https://www.vtk.org/doc/nightly/html/classvtkRenderer.html

                    world_coord = self._vtk_convert_display_coord_to_world_coord(x, y, z_value)
                    world_coords.append(world_coord)
            index += 1

        return world_coords

    def get_z_buffer_as_world_coords(self, n_th_result_point=10):
        """
        Do not confuse z_buffer with depth_buffer!
        z_buffer contains values in [0,1]
        depth_buffer contains the actual distance values
        :param z_buffer_matrix: contains values between 0 and 1.0
        :return:
        """
        z_buffer_matrix = self.get_opengl_z_buffer_as_numpy_arr()
        return self.convert_z_buffer_to_world_coords(z_buffer_matrix, n_th_result_point)

    def get_pixel_z_values_as_world_coords(self,
                                           pixel_z_values,
                                           computer_vision_pixels=True,
                                           none_values_allowed=False):

        """
        computer vision pixels start at the upper left
        :param pixel_z_values:
        :param computer_vision_pixels: computer_vision_pixels start at the upper left
        :return:
        """

        world_coords = []
        coords_without_intersection = 0
        num_values = len(pixel_z_values)
        for index, vec in enumerate(pixel_z_values):
            # if index % 1000 == 0:
            #     logger.info('index: ' + str(index) + ' of ' + str(num_values))
            if vec is None:
                if none_values_allowed:
                    world_coords.append(None)
                else:
                    assert False
            else:
                (x, y, z) = vec
                if z < 1.0:
                    # does not work
                    if computer_vision_pixels:      # rotation around the x axis
                        y = self.render_height - y

                    world_coord = self._vtk_convert_display_coord_to_world_coord(x, y, z)
                    world_coords.append(world_coord)
                else:
                    world_coords.append(None)
                    coords_without_intersection += 1

        return world_coords

    def _vtk_convert_display_coord_to_world_coord(self, x, y, z):

        self.vtk_renderer.SetDisplayPoint(x, y, z)
        self.vtk_renderer.DisplayToWorld()
        world_coord_hom = self.vtk_renderer.GetWorldPoint()
        world_coord_hom = np.asarray(world_coord_hom, dtype=float)
        world_coord_hom /= world_coord_hom[3]
        world_coord = world_coord_hom[0:3]

        return world_coord
