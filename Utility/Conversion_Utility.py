import vtk
import numpy as np

# See:
#   https://pyscience.wordpress.com/2014/09/06/numpy-to-vtk-converting-your-numpy-arrays-to-vtk-arrays-and-files/
#       from vtk.util import numpy_support
#       help(numpy_support)
#       help(numpy_support.numpy_to_vtk)
#       help(numpy_support.vtk_to_numpy)


def convert_rotation_and_translation_to_vtk_matrix(rotation, translation):
    m = vtk.vtkMatrix4x4()
    for r in range(3):
        for c in range(3):
            m.SetElement(r, c, rotation[r][c])
    m.SetElement(0, 3, translation.x())
    m.SetElement(1, 3, translation.y())
    m.SetElement(2, 3, translation.z())
    m.SetElement(3, 3, 1)
    return m


def convert_numpy_array_to_vtk_transform(np_arr):
    list_flattened = [num for row in np_arr.tolist() for num in row]
    vtk_transform = vtk.vtkTransform()
    vtk_transform.SetMatrix(list_flattened)
    return vtk_transform


def convert_numpy_array_to_vtk_matrix(np_arr):
    list_flattened = [num for row in np_arr.tolist() for num in row]
    vtk_matrix = vtk.vtkMatrix4x4()
    vtk_matrix.DeepCopy(list_flattened)
    return vtk_matrix


def convert_vtk_matrix_to_numpy_array(vtk_matrix):
    list_to_be_filled = [0.0] * 16
    # The second parameter is required, since DeepCopy is overloaded
    vtk.vtkMatrix4x4().DeepCopy(list_to_be_filled, vtk_matrix)
    return np.asarray(list_to_be_filled).reshape((4, 4))

