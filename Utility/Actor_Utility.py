import vtk
from VTKInterface.Utility.Data_Utility import DataUtility


class ActorUtility(object):

    """ Usage:
        vtk_renderer = vtk.vtkRenderer()
        actor = PrimitiveInterface.create_line_actor(...)
        vtk_renderer.AddActor(actor)
    """

    @staticmethod
    def create_vtk_line_actor(p1, p2, color):

        line = vtk.vtkLineSource()
        line.SetPoint1(p1)
        line.SetPoint2(p2)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(line.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        return actor

    @staticmethod
    def create_vtk_point_actor(p, color, radius=1.0):
        point = vtk.vtkSphereSource()
        point.SetCenter(p)
        point.SetRadius(radius)
        point.SetPhiResolution(100)
        point.SetThetaResolution(100)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(point.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)

        return actor

    @staticmethod
    def create_vtk_point_cloud_actor(coords, colors=None, opacity=1.0, point_size=3, overwrite_color=None):
        point_cloud_poly_data = DataUtility.create_point_cloud_poly_data(coords, colors)
        return ActorUtility.create_vtk_point_cloud_actor_from_poly_data(
            point_cloud_poly_data, opacity, point_size, overwrite_color)

    @staticmethod
    def create_vtk_point_cloud_actor_from_poly_data(point_cloud_poly_data,
                                                    opacity=1.0,
                                                    point_size=3,
                                                    overwrite_color=None):

        num_points = point_cloud_poly_data.GetNumberOfPoints()
        num_polys = point_cloud_poly_data.GetNumberOfPolys()

        # print("pointcloud.GetNumberOfPoints()", num_points)
        # print("pointcloud.GetNumberOfPolys()", num_polys)

        assert num_points > 0 and num_polys == 0

        vtk_vertices = DataUtility.create_vtk_vertex_array(num_points)
        point_cloud_poly_data.SetVerts(vtk_vertices)
        if overwrite_color is not None:
            vtk_colors = DataUtility.create_vtk_color_array(num_points, overwrite_color)
            point_cloud_poly_data.GetPointData().SetScalars(vtk_colors)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(point_cloud_poly_data)
        mapper.SetScalarVisibility(1)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().SetPointSize(point_size)

        return actor

    @staticmethod
    def create_vtk_mesh_actor_from_poly_data(mesh_poly_data, mesh_texture=None, opacity=1.0):
        # PolyData representing a mesh must contain polygons
        assert mesh_poly_data.GetNumberOfPolys() > 0
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh_poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(opacity)
        if mesh_texture is not None:
            actor.SetTexture(mesh_texture)

        return actor

    @staticmethod
    def create_vtk_mesh_or_point_cloud_actor_from_poly_data(poly_data,
                                                            opacity=1.0,
                                                            mesh_texture=None,
                                                            point_size=3,
                                                            point_overwrite_color=None):
        if poly_data.GetNumberOfPolys() > 0:
            return ActorUtility.create_vtk_mesh_actor_from_poly_data(
                poly_data,
                mesh_texture,
                opacity)
        else:
            return ActorUtility.create_vtk_point_cloud_actor_from_poly_data(
                poly_data,
                opacity=opacity,
                point_size=point_size,
                overwrite_color=point_overwrite_color)

    @staticmethod
    def create_vtk_mesh_or_point_cloud_actor_from_file(poly_ifp, texture_ifp=None):
        poly_data = DataUtility.create_poly_data_from_file(
            poly_ifp)
        if texture_ifp is None:
            texture = None
        else:
            texture = DataUtility.create_texture_from_jpeg(texture_ifp)

        return ActorUtility.create_vtk_mesh_or_point_cloud_actor_from_poly_data(
            poly_data,
            mesh_texture=texture,
            point_overwrite_color=None)

    @staticmethod
    def create_vtk_example_mesh_actor(opacity=1.0):
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetResolution(8)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cylinder.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(opacity)
        return actor

