import radia as rad
import numpy as np
from pkg_resources import resource_stream

import panel as pn
import vtk
import numpy as np

pn.extension('vtk')  # Enable VTK support in Panel


def draw_radia_vtk(
    obj,
    bgcolor=[1, 1, 1],
    windowsize=[800, 600],
    opacity=None,
    faceopacity=None,
    lineopacity=None,
    linewidth=2,
    linecolor=None,
    edgelines=None,
    axes=None,
    faces=None,
    xrange=[None, None],
    yrange=[None, None],
    zrange=[None, None],
):
    """
    Displays a 3D object in JupyterLab using Panel and VTK.

    Parameters:
    - obj: Radia object to be visualized.
    - bgcolor (list): Background color as [R, G, B] in range [0,1]. Default is white.
    - windowsize (list): Window size as [width, height]. Default is [800, 600].
    - opacity (float or None): Global opacity for both faces and lines (if faceopacity/lineopacity are not set).
    - faceopacity (float or None): Opacity of faces (0 = fully transparent, 1 = solid). Overrides `opacity` if set.
    - lineopacity (float or None): Opacity of lines (0 = fully transparent, 1 = solid). Overrides `opacity` if set.
    - linewidth (int): Thickness of the lines. Default is 2.
    - linecolor (list or None): If defined, overrides individual line colors [R, G, B] in range [0,1].
    - edgelines (bool or None): Whether to draw edge lines.
    - axes (bool or None): Whether to draw axes.
    - faces (bool or None): Whether to draw faces.
    - xrange (list): `[xmin, xmax]` to filter displayed elements (default: [None, None]).
    - yrange (list): `[ymin, ymax]` to filter displayed elements (default: [None, None]).
    - zrange (list): `[zmin, zmax]` to filter displayed elements (default: [None, None]).

    Returns:
    - A Panel VTK object for visualization.
    """

    # 🔹 Validate zrange
    if zrange[0] is not None and zrange[1] is not None:
        if zrange[0] >= zrange[1]:
            raise ValueError("Invalid zrange: zrange[0] must be less than zrange[1]")

    # 🔹 Validate input values
    if opacity is not None and not (0 <= opacity <= 1):
        raise ValueError("opacity must be between 0 and 1.")
    if faceopacity is not None and not (0 <= faceopacity <= 1):
        raise ValueError("faceopacity must be between 0 and 1.")
    if lineopacity is not None and not (0 <= lineopacity <= 1):
        raise ValueError("lineopacity must be between 0 and 1.")
    if not isinstance(linewidth, (int, float)) or linewidth <= 0:
        raise ValueError("linewidth must be a positive number.")
    if not all(0 <= c <= 1 for c in bgcolor):
        raise ValueError("Background color values must be in the range [0, 1].")

    # Apply global opacity if faceopacity/lineopacity are not explicitly set
    face_opacity = faceopacity if faceopacity is not None else (opacity if opacity is not None else 1.0)
    line_opacity = lineopacity if lineopacity is not None else (opacity if opacity is not None else 1.0)

    # Ensure at most two of [edgelines, axes, faces] are defined
    defined_flags = [("Axes", axes), ("EdgeLines", edgelines), ("Faces", faces)]
    active_flags = [(name, state) for name, state in defined_flags if state is not None]

    if len(active_flags) > 2:
        raise ValueError("At most two of 'edgelines', 'axes', and 'faces' can be defined.")

    # Construct drawparams string with 'True' and 'False' explicitly formatted
    drawparams = ";".join(f"{name}->{str(state)}" for name, state in active_flags) if active_flags else ""

    # 🔹 Generate data from obj
    data = rad.ObjDrwVTK(obj, drawparams)

    # Extract polygon and line data
    polygon_data = data.get("polygons", {})
    poly_vertices = polygon_data.get("vertices", [])
    poly_lengths = polygon_data.get("lengths", [])
    poly_colors = polygon_data.get("colors", [])

    line_data = data.get("lines", {})
    line_vertices = line_data.get("vertices", [])
    line_lengths = line_data.get("lengths", [])
    line_colors = line_data.get("colors", [])

    # 🔹 Convert polygon vertices into VTK format (Filtering based on zrange)
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()
    poly_colors_array = vtk.vtkUnsignedCharArray()
    poly_colors_array.SetNumberOfComponents(3)  # RGB format
    poly_colors_array.SetName("PolyColors")

    index = 0
    num_faces = len(poly_lengths)

    for i in range(num_faces):
        length = poly_lengths[i]
        face_vertices = [poly_vertices[j:j+3] for j in range(index, index + length * 3, 3)]
        index += length * 3

        # 🔹 Exclude face if any vertex is outside zrange
        if any(
            (xrange[0] is not None and vertex[0] < xrange[0]) or
            (xrange[1] is not None and vertex[0] > xrange[1]) or
            (yrange[0] is not None and vertex[1] < yrange[0]) or
            (yrange[1] is not None and vertex[1] > yrange[1]) or
            (zrange[0] is not None and vertex[2] < zrange[0]) or
            (zrange[1] is not None and vertex[2] > zrange[1]) 
            for vertex in face_vertices
        ):
            continue

        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(length)

        for j, vertex in enumerate(face_vertices):
            points.InsertNextPoint(vertex)
            polygon.GetPointIds().SetId(j, points.GetNumberOfPoints() - 1)

        polys.InsertNextCell(polygon)

        # Assign per-face colors (convert to 0-255)
        r = int(poly_colors[i * 3] * 255)
        g = int(poly_colors[i * 3 + 1] * 255)
        b = int(poly_colors[i * 3 + 2] * 255)
        poly_colors_array.InsertNextTuple3(r, g, b)

    # Create a PolyData object and apply colors
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(polys)
    polydata.GetCellData().SetScalars(poly_colors_array)  # Attach colors

    poly_mapper = vtk.vtkPolyDataMapper()
    poly_mapper.SetInputData(polydata)
    poly_mapper.SetScalarModeToUseCellData()  # Use per-face colors

    poly_actor = vtk.vtkActor()
    poly_actor.SetMapper(poly_mapper)
    poly_actor.GetProperty().SetOpacity(face_opacity)

    # 🔹 Convert line vertices into VTK format (Filtering based on zrange)
    line_points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()
    line_colors_array = vtk.vtkUnsignedCharArray()
    line_colors_array.SetNumberOfComponents(3)
    line_colors_array.SetName("LineColors")

    index = 0
    num_lines = len(line_lengths)

    for i in range(num_lines):
        length = line_lengths[i]
        line_vertices_group = [line_vertices[j:j+3] for j in range(index, index + length * 3, 3)]
        index += length * 3

        # 🔹 Exclude line if any vertex is outside zrange
        if any(
            (xrange[0] is not None and vertex[0] < xrange[0]) or
            (xrange[1] is not None and vertex[0] > xrange[1]) or
            (yrange[0] is not None and vertex[1] < yrange[0]) or
            (yrange[1] is not None and vertex[1] > yrange[1]) or
            (zrange[0] is not None and vertex[2] < zrange[0]) or
            (zrange[1] is not None and vertex[2] > zrange[1])
            for vertex in line_vertices_group
        ):
            continue

        line = vtk.vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(length)

        for j, vertex in enumerate(line_vertices_group):
            line_points.InsertNextPoint(vertex)
            line.GetPointIds().SetId(j, line_points.GetNumberOfPoints() - 1)

        lines.InsertNextCell(line)

        # Apply override color if defined, otherwise use original line colors
        r, g, b = [int(c * 255) for c in (linecolor if linecolor else line_colors[i * 3: i * 3 + 3])]
        line_colors_array.InsertNextTuple3(r, g, b)

    # Create a PolyData object for lines
    line_polydata = vtk.vtkPolyData()
    line_polydata.SetPoints(line_points)
    line_polydata.SetLines(lines)
    line_polydata.GetCellData().SetScalars(line_colors_array)

    line_mapper = vtk.vtkPolyDataMapper()
    line_mapper.SetInputData(line_polydata)

    line_actor = vtk.vtkActor()
    line_actor.SetMapper(line_mapper)
    line_actor.GetProperty().SetLineWidth(linewidth)
    line_actor.GetProperty().SetOpacity(line_opacity)

    # Renderer setup
    renderer = vtk.vtkRenderer()
    renderer.AddActor(poly_actor)
    renderer.AddActor(line_actor)
    renderer.SetBackground(*bgcolor)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(*windowsize)

    vtk_pane = pn.pane.VTK(render_window, width=windowsize[0], height=windowsize[1])

    return pn.Column(vtk_pane)


def get_beff (Z, By, nperiods=None, harmonics=False, debug=False):
    """
    Get the effective bfield based on the input field.  Input data must be correspond to 
    an integer number of periods.
    
    Z : list of z positions
    By: list of vertical field values corresponding to each z in Z
    nperiods: Number of periods present in the data given
    harmonics: if True return odd harmonics instead of beff
    debug: if True print debug info
    """
    n = len(By)
    freqs = np.fft.fftfreq(n)
    mask = freqs > 0

    fft_vals = np.fft.fft(By)
    fft_theo = 2 * np.abs(fft_vals/n)

    # If nperiods is not specified, just find the fundamental and scale
    if nperiods is None:
        nperiods = np.argmax(fft_theo[mask]) + 1
    if debug: print('nperiods:', nperiods)

    period = np.abs(Z[-1] - Z[0]) / nperiods
    if debug: print('get_beff period', period)

    beff = 0
    bharmonics = []
    for i in range(nperiods-1, len(fft_theo[mask])//2, 2*nperiods):
        h = (i // nperiods) * 2 + 1

        if debug and h < 15: print(i, h, fft_theo[mask][i])

        beff += (fft_theo[mask][i]/h)**2
        bharmonics.append(fft_theo[mask][i])

    if harmonics:
        return bharmonics
    return np.sqrt(beff)

def b2k_mm (b, period):
    """Convert magnetic field to K where period is in mm"""
    return 0.09336*b*period

def get_magnetic_material_permendur ():
    return get_magnetic_material(filename=resource_stream (__name__,'data/PermendurNEOMAX.txt'))

def get_magnetic_material (filename):
    '''
    Get magnetic material defined by bh curve in file
    '''
    # Setup permendur material for radia
    Permendur = np.loadtxt(filename)
    HP = [x[0] for x in Permendur]
    BP = [x[1] for x in Permendur]

    # H(Oe) vs B(G) to myu0*H(A/m) vs myu0*M(T)=B(T)-myu0*H(A/m)
    myu0 = 4e-7 * np.pi

    # conversion factor between oersted and A/m
    conversion = 1000 / 4 / np.pi

    radHP = [conversion * myu0 * x for x in HP]
    radMP = [1e-4 * x[1] - x[0] for x in zip(radHP, BP)]
    radHMP = [[x[0], x[1]] for x in zip(radHP, radMP)]
    return rad.MatSatIsoTab(radHMP)


