import vtk
from VTKInterface.Interfaces.Camera_Interface import CameraInterface
from VTKInterface.Interfaces.ZBuffer_Interface import ZBufferInterface
from VTKInterface.Interfaces.Coordinate_Axes_Interface import CoordinateAxesInterface

from VTKInterface.Utility.Actor_Utility import ActorUtility


class RenderInterface(CameraInterface, ZBufferInterface, CoordinateAxesInterface):

    # https://www.kitware.com/products/books/VTKUsersGuide.pdf
    #       4.4 Controlling The Camera

    def __init__(self, off_screen_rendering=True, width=None, height=None, background_color=(0, 0, 255)):

        print(
            'VTK Version: ' +
            str(vtk.vtkVersion.GetVTKMajorVersion()) + '.' +
            str(vtk.vtkVersion.GetVTKMinorVersion()))

        self.vtk_renderer = vtk.vtkRenderer()

        self.vtk_render_window = vtk.vtkRenderWindow()
        CameraInterface.__init__(
            self, self.vtk_renderer, self.vtk_render_window)
        ZBufferInterface.__init__(
            self, self.vtk_renderer, self.vtk_render_window, width, height)

        self.vtk_axes_actor = vtk.vtkAxesActor()
        self.vtk_orientation_marker_widget = vtk.vtkOrientationMarkerWidget()
        self.vtk_render_window_interactor = vtk.vtkRenderWindowInteractor()
        CoordinateAxesInterface.__init__(
            self,
            self.vtk_renderer,
            self.vtk_axes_actor,
            self.vtk_orientation_marker_widget,
            self.vtk_render_window_interactor)

        self.vtk_render_window.SetOffScreenRendering(off_screen_rendering)
        self.vtk_render_window.AddRenderer(self.vtk_renderer)

        if not off_screen_rendering:
            self._init_render_window_interactor()

        # Configure Render Settings
        self.vtk_renderer.SetBackground(*background_color)
        if width is not None and height is not None:
            self.render_width = width
            self.render_height = height
            self.vtk_render_window.SetSize(width, height)

        self.set_active_cam_model_view_transformation_to_identity()

    def _init_render_window_interactor(self):
        self.vtk_render_window_interactor = vtk.vtkRenderWindowInteractor()
        self.vtk_render_window_interactor.SetRenderWindow(self.vtk_render_window)
        self.set_interaction_style()
        self.vtk_render_window_interactor.Initialize()

    def add_actor(self, actor):
        self.vtk_renderer.AddActor(actor)

    def add_point_cloud(self, coords, colors=None):
        point_cloud_actor = ActorUtility.create_vtk_point_cloud_actor(coords, colors)
        self.add_actor(point_cloud_actor)

    def load_vtk_mesh_or_point_cloud(self, poly_ifp, texture_ifp=None):
        actor = ActorUtility.create_vtk_mesh_or_point_cloud_actor_from_file(
            poly_ifp, texture_ifp)
        self.vtk_renderer.AddActor(actor)

    def get_render_window(self):
        return self.vtk_render_window

    def set_interaction_style(self):

        # Change the usage style of the interactor
        # http://www.vtk.org/doc/nightly/html/classvtkInteractorStyle.html
        # interactor_style = vtk.vtkContextInteractorStyle()  # No interaction at all
        # interactor_style = vtk.vtkInteractorStyle3D()  # Crashes
        # interactor_style = vtk.vtkInteractorStyleDrawPolygon()  # Not useful in viewing context
        # interactor_style = vtk.vtkInteractorStyleFlight()  # Unintuitive
        # interactor_style = vtk.vtkInteractorStyleJoystickActor()  # Intuitive, but changes the scene (camera is fixed)
        # interactor_style = vtk.vtkInteractorStyleJoystickCamera()  # Intuitive, does change the camera, but not so handy
        # interactor_style = vtk.vtkInteractorStyleRubberBand2D()  # Not useful in viewing context
        # interactor_style = vtk.vtkInteractorStyleRubberBandZoom()  # zooming can not be undone
        # interactor_style = vtk.vtkInteractorStyleSwitchBase()  # Intuitive, does change the camera, but not so handy
        # interactor_style = vtk.vtkInteractorStyleTerrain()  # Not that bad
        # interactor_style = vtk.vtkInteractorStyleTrackballActor()  # Intiutive, but changes the scene (camera is fixed)
        # interactor_style = vtk.vtkInteractorStyleTrackballCamera()  # THATS IT
        # interactor_style = vtk.vtkInteractorStyleUnicam()  # not so useful
        # interactor_style = vtk.vtkInteractorStyleUser()  # no interaction at all

        interactor_style = vtk.vtkInteractorStyleTrackballCamera()  # THATS IT
        self.vtk_render_window_interactor.SetInteractorStyle(interactor_style)

    def render(self):
        # Never call the render method of the renderer,
        # always use the renderwindow render method
        self.vtk_render_window.Render()

    def start_interactor(self):
        self.vtk_render_window_interactor.Start()

    def render_and_start(self):
        self.render()
        self.start_interactor()

