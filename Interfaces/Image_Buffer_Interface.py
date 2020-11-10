
import numpy as np
from Utility.Logging_Extension import logger
from matplotlib import pyplot as plt

import vtk
from vtk.util import numpy_support

from VTKInterface.Interfaces.Base_Interface import BaseInterface
from VTKInterface.Utility.Data_Utility import DataUtility


class ImageBufferInterface(BaseInterface):

    def __init__(self, vtk_renderer=None, vtk_render_window=None, width=None, height=None):

        self.init_instance_variable(
            "vtk_renderer", vtk_renderer, vtk.vtkRenderer())
        self.init_instance_variable(
            "vtk_render_window", vtk_render_window, vtk.vtkRenderWindow())

        self.width = width
        self.height = height

    def get_rgba_buffer_as_numpy_arr(self):

        if not self.vtk_render_window.GetOffScreenRendering():
            error_str = 'THIS ONLY WORKS IN OFF SCREEN MODE ' \
                        '(use off_screen_rendering=True in render_interface constructor)'
            assert False, error_str
        # https://stackoverflow.com/questions/14553523/vtk-render-window-image-to-numpy-array

        # http://berkgeveci.github.io/page7/
        rgba_data = vtk.vtkFloatArray()
        # GetZbufferData (int x, int y, int x2, int y2, vtkFloatArray *z)

        blend_value = 0
        self.vtk_render_window.GetRGBAPixelData(
            0, 0, self.render_width - 1, self.render_height - 1, blend_value, rgba_data)
        rgba_data_numpy = numpy_support.vtk_to_numpy(rgba_data)
        rgba_data_numpy = np.reshape(rgba_data_numpy, (self.render_height, self.render_width, 4))
        rgba_data_numpy = np.flipud(rgba_data_numpy)
        return rgba_data_numpy

    def show_rgba_buffer(self):
        color_image = self.get_rgba_buffer_as_numpy_arr()
        plt.imshow(color_image)
        plt.show()
