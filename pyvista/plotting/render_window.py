"""Wrap render window for pyvista."""

from pyvista._vtk import vtkRenderWindow

# ren = vtkRenderWindow()
# GetOffScreenFramebuffer

class RenderWindow(vtkRenderWindow):
    """Wrap VTK render window for pyvista."""

    def __init__(self, multi_samples, borders=True,
                 line_smoothing=False, point_smoothing=False,
                 polygon_smoothing=False, off_screen=False,
                 renderers=None):
        """Initialize render window."""
        self.SetMultiSamples(multi_samples)
        self.SetBorders(borders)
        self.SetLineSmoothing(line_smoothing)
        self.SetPointSmoothing(point_smoothing)
        self.SetPolygonSmoothing(polygon_smoothing)
        self.off_screen = off_screen
        self._shadow_renderer = None
        self._had_background_layer = False

        for renderer in renderers:
            self.add_renderer(renderer)

    @property
    def full_screen(self):
        """Return or set the state of full-screen."""
        return self.GetFullScreen()

    @full_screen.setter
    def full_screen(self, full_screen):
        self.SetFullScreen(full_screen)

    @property
    def borders(self):
        """Return or set the render window borders."""
        return self.GetBorders()

    @borders.setter
    def borders(self, borders):
        self.SetBorders(borders)

    @property
    def off_screen(self):
        """Return or set off-screen rendering."""
        return self.GetOffScreenRendering()

    @off_screen.setter
    def off_screen(self, value):
        self.SetOffScreenRendering(value)

    def add_renderer(self, renderer):
        """Add a renderer."""
        self.AddRenderer(renderer)

    @property
    def n_layers(self):
        """Return or set the number of layers."""
        return self.GetNumberOfLayers()

    @n_layers.setter
    def n_layers(self, n_layers):
        self.SetNumberOfLayers(n_layers)

    @property
    def alpha_bit_planes(self):
        """Return or set the use of alpha bitplanes."""
        return self.GetAlphaBitPlanes()

    @alpha_bit_planes.setter
    def alpha_bit_planes(self, value):
        self.SetAlphaBitPlanes(value)

    @property
    def size(self):
        """Return or set the size of the render window."""
        return list(self.GetSize())

    @size.setter
    def size(self, size):
        self.SetSize(size[0], size[1])

    def render(self):
        """Render this render window."""
        self.Render()

    def check_offscreen_framebuffer(self):
        """Check for the off screen framebuffer."""
        if hasattr(self, 'GetOffScreenFramebuffer'):
            if not self.GetOffScreenFramebuffer().GetFBOIndex():
                # must raise a runtime error as this causes a segfault on VTK9
                raise ValueError('Invoking helper with no framebuffer')

    def finalize(self):
        """Finalize the render window."""
        self.Finalize()

    @property
    def renderers(self):
        """Return a list of all renderers"""
        renderers = []
        coll = self.GetRenderers()
        for i in range(coll.GetNumberOfItems()):
            renderers.append(coll.GetItemAsObject(i))
        return renderers

    def add_shadow_renderer(self, renderer):
        """Add a shadow renderer"""
        self._shadow_renderer = renderer
        self.add_renderer(renderer)

    def add_background_layer(self):
        """Add a background layer to the render window.

        Does nothing if background layer already exists.

        """
        if self._had_background_layer:
            return

        # Need to change the number of layers to support an additional
        # background layer
        self.n_layers += 1
        self._had_background_layer = True
