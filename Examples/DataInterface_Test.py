
from VTKInterface.Utility.Data_Utility import DataUtility

ply_ifp = 'Example.ply'
ply_ofp = 'Example_color.ply'

poly_data = DataUtility.create_poly_data_from_ply(ply_ifp)

# Option 1: Use default colors
vtk_colors = poly_data.GetPointData().GetScalars()

# Option 2: Overwrite default colors
vtk_colors = DataUtility.create_vtk_color_array(
    size=poly_data.GetNumberOfPoints(),
    color=[255, 255, 0])

poly_data.GetPointData().SetScalars(vtk_colors)
DataUtility.write_poly_data_to_ply(poly_data, ply_ofp)


