import numpy as np
import vtk

from VTKInterface.Utility.Actor_Utility import ActorUtility
from VTKInterface.Utility.Conversion_Utility import convert_numpy_array_to_vtk_transform
from VTKInterface.Interfaces.Base_Interface import BaseInterface


class CoordinateAxesInterface(BaseInterface):

    def __init__(self,
                 vtk_renderer=None,
                 vtk_axes_actor=None,
                 vtk_orientation_marker_widget=None,
                 vtk_render_window_interactor=None):

        self.init_instance_variable(
            "vtk_renderer", vtk_renderer, vtk.vtkRenderer())
        self.init_instance_variable(
            "vtk_axes_actor", vtk_axes_actor, vtk.vtkAxesActor())
        self.init_instance_variable(
            "vtk_orientation_marker_widget", vtk_orientation_marker_widget, vtk.vtkOrientationMarkerWidget())
        self.init_instance_variable(
            "vtk_render_window_interactor", vtk_render_window_interactor, vtk.vtkRenderWindowInteractor())

    def show_global_coordinate_axes_widget(self):

        self.vtk_orientation_marker_widget.SetOutlineColor(0.9300, 0.5700, 0.1300)
        self.vtk_orientation_marker_widget.SetOrientationMarker(self.vtk_axes_actor)
        self.vtk_orientation_marker_widget.SetInteractor(self.vtk_render_window_interactor)
        # self.vtk_orientation_marker_widget.SetViewport(0.0, 0.0, 0.4, 0.4)
        self.vtk_orientation_marker_widget.SetEnabled(1)
        self.vtk_orientation_marker_widget.InteractiveOn()

    def add_coordinate_axes(self, transformation_mat, no_labels=True):

        # https://www.vtk.org/Wiki/VTK/Examples/Python/GeometricObjects/Display/Axes
        vtk_transform = convert_numpy_array_to_vtk_transform(transformation_mat)

        axes_actor = vtk.vtkAxesActor()
        axes_actor.SetUserTransform(vtk_transform)

        if no_labels:
            axes_actor.SetXAxisLabelText("")
            axes_actor.SetYAxisLabelText("")
            axes_actor.SetZAxisLabelText("")
        else:
            # https://vtk.org/doc/nightly/html/classvtkCaptionActor2D.html
            # https://vtk.org/doc/nightly/html/classvtkTextProperty.html
            x_axis_text_property = axes_actor.GetXAxisCaptionActor2D().GetCaptionTextProperty()
            y_axis_text_property = axes_actor.GetYAxisCaptionActor2D().GetCaptionTextProperty()
            z_axis_text_property = axes_actor.GetZAxisCaptionActor2D().GetCaptionTextProperty()

            x_axis_text_property.SetColor(1, 0, 0)
            y_axis_text_property.SetColor(0, 1, 0)
            z_axis_text_property.SetColor(0, 0, 1)
            for prop in [x_axis_text_property, y_axis_text_property, z_axis_text_property]:
                prop.SetBold(0)

            # Changing the font size has no effect
            # print(x_axis_text_property.GetFontSize())
            # x_axis_text_property.SetFontSize(0)
            # print(x_axis_text_property.GetFontSize())

            # y_axis_text_property.SetFontSize(0, 1, 0)
            # z_axis_text_property.SetFontSize(0, 0, 1)

        self.vtk_renderer.AddActor(axes_actor)

    def vtk_add_point(self, p, color, radius=1.0):
        self.vtk_renderer.AddActor(
            ActorUtility.create_vtk_point_actor(p, color, radius)
        )

    def vtk_add_line(self, p1, p2, color, line_width=5):
        actor = ActorUtility.create_vtk_line_actor(p1, p2, color=color)
        actor.GetProperty().SetLineWidth(line_width)
        self.vtk_renderer.AddActor(actor)

    def add_coordinate_axes_custom(self,
                                   cam_to_world_mat_computer_vision,
                                   length=2,
                                   line_width=1,
                                   point_radius=0.05,
                                   add_center=False,
                                   add_endpoints=False):

        nc = vtk.vtkNamedColors()
        green = nc.GetColor3ub('Lime')
        red = nc.GetColor3ub('red')
        blue = nc.GetColor3ub('blue')
        black = nc.GetColor3ub('black')

        # Same coordinate system than blender
        origin_cam = (0, 0, 0)
        x_dir_cam = (length, 0, 0)
        y_dir_cam = (0, length, 0)
        z_dir_cam = (0, 0, length)

        origin_world = cam_to_world_mat_computer_vision.dot(np.append(np.array(origin_cam), [1]))[0:3]
        x_dir_world = cam_to_world_mat_computer_vision.dot(np.append(np.array(x_dir_cam), [1]))[0:3]
        y_dir_world = cam_to_world_mat_computer_vision.dot(np.append(np.array(y_dir_cam), [1]))[0:3]
        z_dir_world = cam_to_world_mat_computer_vision.dot(np.append(np.array(z_dir_cam), [1]))[0:3]

        self.vtk_add_line(origin_world, x_dir_world, color=red, line_width=line_width)
        self.vtk_add_line(origin_world, y_dir_world, color=green, line_width=line_width)
        self.vtk_add_line(origin_world, z_dir_world, color=blue, line_width=line_width)

        if add_center:
            self.vtk_add_point(origin_world, radius=point_radius, color=black)

        if add_endpoints:
            # https://www.vtk.org/Wiki/VTK/Examples/Python/GeometricObjects/Display/Axes
            self.vtk_add_point(x_dir_world, radius=point_radius, color=red)
            self.vtk_add_point(y_dir_world, radius=point_radius, color=green)
            self.vtk_add_point(z_dir_world, radius=point_radius, color=blue)

