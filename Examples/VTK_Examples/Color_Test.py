
import vtk

# https://cmake.org/Wiki/VTK/Examples/Python/Visualization/NamedColors
# https://vtk.org/doc/nightly/html/classvtkNamedColors.html
# https://vtk.org/Wiki/VTK/Examples/Python/Visualization/VTKNamedColorPatches_html

nc = vtk.vtkNamedColors()
colorNames = nc.GetColorNames().split('\n')
print("There are", len(colorNames), "colors:")
print(colorNames)
syn = nc.GetSynonyms().split('\n\n')
synonyms = []
for ele in syn:
    synonyms.append(ele.split('\n'))
print("There are", len(synonyms), "synonyms:")
print(synonyms)

print("nc.GetColor('green'):", nc.GetColor3ub('Lime'))
print("nc.GetColor('red'):", nc.GetColor3ub('red'))
print("nc.GetColor('blue'):", nc.GetColor3ub('blue'))

