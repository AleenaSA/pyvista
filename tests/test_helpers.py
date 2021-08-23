import os
import pytest
import trimesh
import numpy as np
from PIL import Image
import vtk

import pyvista
from pyvista import _vtk

def test_wrap_none():
    # check against the "None" edge case
    assert pyvista.wrap(None) is None


def test_wrap_pyvista_ndarray(sphere):
    pd = pyvista.wrap(sphere.points)
    assert isinstance(pd, pyvista.PolyData)


# NOTE: It's not necessary to test all data types here, several of the
# most used ones.  We're just checking that we can wrap VTK data types.
@pytest.mark.parametrize('dtypes', [(np.float64, _vtk.vtkDoubleArray),
                                    (np.float32, _vtk.vtkFloatArray),
                                    (np.int64, _vtk.vtkTypeInt64Array),
                                    (np.int32, _vtk.vtkTypeInt32Array),
                                    (np.int8, _vtk.vtkSignedCharArray),
                                    (np.uint8, _vtk.vtkUnsignedCharArray),
                                    ])
def test_wrap_pyvista_ndarray_vtk(dtypes):
    np_dtype, vtk_class = dtypes
    np_array = np.array([[0, 10, 20],
                         [-10, -200, 0],
                         [0.5, 0.667, 0]], dtype=np_dtype)

    vtk_array = vtk_class()
    vtk_array.SetNumberOfComponents(3)
    vtk_array.SetNumberOfValues(9)
    for i in range(9):
        vtk_array.SetValue(i, np_array.ravel()[i])

    wrapped = pyvista.wrap(vtk_array)
    assert np.allclose(wrapped, np_array)
    assert wrapped.dtype == np_array.dtype


def test_wrap_trimesh():
    points = [[0, 0, 0], [0, 0, 1], [0, 1, 0]]
    faces = [[0, 1, 2]]
    tmesh = trimesh.Trimesh(points, faces=faces, process=False)
    mesh = pyvista.wrap(tmesh)
    assert isinstance(mesh, pyvista.PolyData)

    assert np.allclose(tmesh.vertices, mesh.points)
    assert np.allclose(tmesh.faces, mesh.faces[1:])


def test_make_tri_mesh(sphere):
    with pytest.raises(ValueError):
        pyvista.make_tri_mesh(sphere.points, sphere.faces)

    with pytest.raises(ValueError):
        pyvista.make_tri_mesh(sphere.points[:, :1], sphere.faces)

    faces = sphere.faces.reshape(-1, 4)[:, 1:]
    mesh = pyvista.make_tri_mesh(sphere.points, faces)

    assert np.allclose(sphere.points, mesh.points)
    assert np.allclose(sphere.faces, mesh.faces)


def test_wrappers():
    vtk_data = vtk.vtkPolyData()
    pv_data = pyvista.wrap(vtk_data)
    assert isinstance(pv_data, pyvista.PolyData)

    class Foo(pyvista.PolyData):
        """A user defined subclass of pyvista.PolyData."""
        pass

    default_wrappers = pyvista._wrappers.copy()
    # Use try...finally to set and reset _wrappers
    try:
        pyvista._wrappers['vtkPolyData'] = Foo

        pv_data = pyvista.wrap(vtk_data)
        assert isinstance(pv_data, Foo)

        tri_data = pv_data.delaunay_2d()

        assert isinstance(tri_data, Foo)

        uniform_grid = pyvista.UniformGrid()
        surface = uniform_grid.extract_surface()

        assert isinstance(surface, Foo)

        surface.delaunay_2d(inplace=True)
        assert isinstance(surface, Foo)

        sphere = pyvista.Sphere()
        assert isinstance(sphere, Foo)

        circle = pyvista.Circle()
        assert isinstance(circle, Foo)

    finally:
        pyvista._wrappers = default_wrappers  # always reset back to default


def test_inheritance_no_wrappers():
    class Foo(pyvista.PolyData):
        pass

    # inplace operations do not change type
    mesh = Foo(pyvista.Sphere())
    mesh.decimate(0.5, inplace=True)
    assert isinstance(mesh, Foo)

    # without using _wrappers, we need to explicitly handle inheritance
    mesh = Foo(pyvista.Sphere())
    new_mesh = mesh.decimate(0.5)  
    assert isinstance(new_mesh, pyvista.PolyData)
    foo_new_mesh = Foo(new_mesh)
    assert isinstance(foo_new_mesh, Foo)


def test_skybox(tmpdir):
    path = str(tmpdir.mkdir("tmpdir"))
    sets = ['posx', 'negx', 'posy', 'negy', 'posz', 'negz']
    for suffix in sets:
        image = Image.new('RGB', (10, 10))
        image.save(os.path.join(path, suffix + '.jpg'))

    skybox = pyvista.cubemap(path)
    assert isinstance(skybox, pyvista.Texture)

    with pytest.raises(FileNotFoundError, match='Unable to locate'):
        pyvista.cubemap('')
