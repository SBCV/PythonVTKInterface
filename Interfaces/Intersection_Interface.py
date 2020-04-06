import numpy as np
import vtk

from VTKInterface.Utility.Data_Utility import DataUtility


class IntersectionInterface(object):

    def __init__(self, mesh):

        self.mesh = mesh
        self.obb_tree = vtk.vtkOBBTree()
        self.obb_tree.SetDataSet(self.mesh)
        self.obb_tree.BuildLocator()

        self.bb_corners = self.get_bounding_box_corner_points()

    @classmethod
    def init_from_file(cls, ifp):
        poly_data = DataUtility.create_poly_data_from_file(
            ifp)
        return IntersectionInterface(poly_data)

    def get_bounds(self):
        return self.mesh.GetBounds()

    def get_bounding_box_corner_points(self):
        bounds = self.mesh.GetBounds()
        x_min, x_max, y_min, y_max, z_min, z_max = bounds
        return np.asarray(
            [(x_min, y_min, z_min),
             (x_min, y_min, z_max),
             (x_min, y_max, z_min),
             (x_min, y_max, z_max),
             (x_max, y_min, z_min),
             (x_max, y_min, z_max),
             (x_max, y_max, z_min),
             (x_max, y_max, z_max)], dtype=float)

    def compute_max_distance_upper_bound(self, query_point):
        if self.bb_corners is None:
            self.bb_corners = self.get_bounding_box_corner_points()
        distances = [np.linalg.norm(bb_corner - query_point) for bb_corner in self.bb_corners]
        max_distance = max(distances)
        return max_distance

    def compute_rays_mesh_intersections(self, rays):

        intersections = [self.compute_first_single_ray_mesh_intersection(ray) for ray in rays]
        intersections = [element for element in intersections if element is not None]
        return intersections

    def compute_first_single_ray_mesh_intersection(self, ray):

        intersection_points = self.compute_single_ray_mesh_intersections_sorted(ray)
        if len(intersection_points) == 0:
            return None

        # The returned intersection points are already sorted, no distance computation necessary
        closest_point = intersection_points[0]
        # for point in intersection_points:
        #     if np.linalg.norm(point - ray.pos_vec) < np.linalg.norm(closest_point - ray.pos_vec):
        #         closest_point = point
        return closest_point

    def compute_single_line_mesh_intersection(self, line_first_point, line_second_point):

        intersection_vtk_points = vtk.vtkPoints()

        #perform ray-casting (intersect a line with the mesh)
        code = self.obb_tree.IntersectWithLine(
            line_first_point,
            line_second_point,
            intersection_vtk_points,
            None)

        # Interpret the 'code'.
        #   If code == 0 is returned then no intersections points were found so return an empty list
        #   If code == -1 then 'pointRaySource' lies outside the surface

        points_vtk_intersection_data = intersection_vtk_points.GetData()
        number_points_intersection = points_vtk_intersection_data.GetNumberOfTuples()
        points_intersection_list = [points_vtk_intersection_data.GetTuple3(idx) for idx in range(
            number_points_intersection)]

        return points_intersection_list

    def compute_single_ray_mesh_intersections_sorted(self, ray):

        intersection_max_distance = self.compute_max_distance_upper_bound(ray.pos_vec)
        line_second_point = ray.pos_vec + intersection_max_distance * ray.dir_vec

        return self.compute_single_line_mesh_intersection(ray.pos_vec, line_second_point)

    def scale_mesh(self, scale):

        transform = vtk.vtkTransform()
        transform_filter = vtk.vtkTransformPolyDataFilter()
        # assuming uniform scale
        transform.Scale(scale, scale, scale)
        transform_filter.SetInputData(self.mesh)
        transform_filter.SetTransform(transform)
        # update to apply the transformation
        transform_filter.Update()

        # replace the existing 'mesh' with the scaled mesh
        self.mesh = transform_filter.GetOutput()
        # update the caster, since 'mesh' changed
        self.obb_tree.SetDataSet(self.mesh)
        self.obb_tree.BuildLocator()



