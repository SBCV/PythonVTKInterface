import os
import vtk

from matplotlib import pyplot as plt


class DataUtility(object):

    # https://www.vtk.org/doc/nightly/html/classvtkPolyDataAlgorithm.html
    # https://www.vtk.org/doc/nightly/html/classvtkPolyData.html
    #   GetVerts ()
    #   GetPolys ()

    @staticmethod
    def create_vtk_color_array(size, color):
        vtk_colors = vtk.vtkUnsignedCharArray()
        vtk_colors.SetName('RGB')
        vtk_colors.SetNumberOfComponents(3)
        for k in range(size):
            vtk_colors.InsertNextTuple3(*color)

        vtk_colors.Modified()
        return vtk_colors

    @staticmethod
    def create_vtk_vertex_array(size):

        vtk_vertices = vtk.vtkCellArray()
        for k in range(size):
            vtk_vertices.InsertNextCell(1)
            vtk_vertices.InsertCellPoint(k)

        vtk_vertices.Modified()
        return vtk_vertices

    @staticmethod
    def create_point_cloud_poly_data(coords, colors=None):

        if colors is None:
            colors = [[1, 1, 1] for coord in coords]

        point_cloud_poly_data = vtk.vtkPolyData()

        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()

        uchar_array = vtk.vtkUnsignedCharArray()
        uchar_array.SetNumberOfComponents(3)
        uchar_array.SetName('ColorArray')

        for coord, color in zip(coords, colors):
            pointId = points.InsertNextPoint(coord[:])

            uchar_array.InsertNextTuple3(*color)

            cells.InsertNextCell(1)
            cells.InsertCellPoint(pointId)

            cells.Modified()
            points.Modified()
            uchar_array.Modified()

        point_cloud_poly_data.SetPoints(points)
        point_cloud_poly_data.SetVerts(cells)

        point_cloud_poly_data.GetPointData().SetScalars(uchar_array)
        return point_cloud_poly_data

    @staticmethod
    def create_poly_data_from_file(poly_ifp):

        # VTK supports only OBJ, PLY and STL, see:
        #   https://vtk.org/doc/nightly/html/classvtkAbstractPolyDataReader.html

        if os.path.splitext(poly_ifp)[1].upper() == '.PLY':
            return DataUtility.create_poly_data_from_ply(poly_ifp)
        elif os.path.splitext(poly_ifp)[1].upper() == '.OBJ':
            return DataUtility.create_poly_data_from_obj(poly_ifp)
        elif os.path.splitext(poly_ifp)[1].upper() == '.STL':
            return DataUtility.create_poly_data_from_stl(poly_ifp)
        else:
            assert False

    @staticmethod
    def create_poly_data_from_stl(stl_ifp):
        reader_stl = vtk.vtkSTLReader()            # Returns vtkPolyData
        reader_stl.SetFileName(
            stl_ifp)
        reader_stl.Update()
        poly_data = reader_stl.GetOutput()
        if poly_data.GetNumberOfPoints() == 0:
            raise ValueError(
                "No point data could be loaded from '" + stl_ifp)
            return None
        return poly_data

    @staticmethod
    def create_poly_data_from_obj(obj_ifp):

        # In contrast to PLY, OBJ-files store the color information as textures, see
        #   https://public.kitware.com/pipermail/vtkusers/2012-January/072082.html

        reader_obj = vtk.vtkOBJReader()          # Returns vtkPolyData
        reader_obj.SetFileName(obj_ifp)
        reader_obj.Update()
        poly_data = reader_obj.GetOutput()
        if poly_data.GetNumberOfPoints() == 0:
            raise ValueError("No point data could be loaded from '" + obj_ifp)
            return None
        return poly_data

    @staticmethod
    def create_poly_data_from_ply(ply_ifp, report_statistics=True):

        # The color information is stored in
        #       vtk_colors = poly_data.GetPointData().GetScalars()
        # In order to modify the colors use
        #       poly_data.GetPointData().SetScalars(vtk_colors)

        reader_ply = vtk.vtkPLYReader()          # Returns vtkPolyData
        reader_ply.SetFileName(ply_ifp)
        reader_ply.Update()
        poly_data = reader_ply.GetOutput()
        if report_statistics:
            print('Number of points: ' + str(poly_data.GetNumberOfPoints()))
            print('Number of polys: ' + str(poly_data.GetNumberOfPolys()))

        if poly_data.GetNumberOfPoints() == 0:
            raise ValueError("No point data could be loaded from '" + ply_ifp)
            return None

        return poly_data

    @staticmethod
    def create_texture_from_jpeg(jpeg_ifp):
        reader_jpeg = vtk.vtkJPEGReader()
        reader_jpeg.SetFileName(jpeg_ifp)
        reader_jpeg.Update()
        texture = vtk.vtkTexture()
        texture.SetInputData(reader_jpeg.GetOutput())
        texture.InterpolateOn()
        return texture

    @staticmethod
    def write_poly_data_to_ply(poly_data, ply_ofp):
        vtk_image_writer = vtk.vtkPLYWriter()
        vtk_image_writer.SetFileName(ply_ofp)
        vtk_image_writer.SetArrayName("RGB")
        vtk_image_writer.SetInputData(poly_data)
        vtk_image_writer.Write()


