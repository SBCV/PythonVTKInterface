import numpy as np
from Utility.Types.Ray import Ray
from VTKInterface.Interfaces.Intersection_Interface import IntersectionInterface
from VTKInterface.Interfaces.Render_Interface import RenderInterface
from VTKInterface.Utility.Actor_Utility import ActorUtility

if __name__ == '__main__':

    poly_ifp = 'mesh_ifp.obj'
    mesh_intersector = IntersectionInterface.init_from_file(poly_ifp)

    pos_vec = np.array([0.0, 0.0, 0.0], dtype=float)
    dir_vec = np.array([0.0, 1.0, 0.0], dtype=float)

    ray = Ray(pos_vec, dir_vec)

    points_intersection = mesh_intersector.compute_single_ray_mesh_intersections_sorted(ray)
    print('points_intersection', points_intersection)

    renderer_interface = RenderInterface(
        off_screen_rendering=False,
        width=1920,
        height=1080,
        background_color=(0, 127, 127))

    renderer_interface.add_actor(
        ActorUtility.create_vtk_point_actor(
            pos_vec, radius=0.5, color=[1.0, 0.0, 0.0]))

    renderer_interface.add_actor(
        ActorUtility.create_vtk_mesh_actor_from_poly_data(mesh_intersector.mesh))

    for p in points_intersection:
        renderer_interface.add_actor(
            ActorUtility.create_vtk_point_actor(p, radius=0.5, color=[0.0, 0.0, 1.0]))

    renderer_interface.render_and_start()
