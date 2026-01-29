"""Basic 3D primitive shapes."""

import numpy as np
from stl import mesh


def cube(size: float = 10.0, center: tuple[float, float, float] = (0, 0, 0)) -> mesh.Mesh:
    """
    Create a cube mesh.

    Args:
        size: Length of each side
        center: Center point (x, y, z)

    Returns:
        mesh.Mesh: The cube mesh
    """
    # Define the 8 vertices of the cube
    half_size = size / 2.0
    cx, cy, cz = center

    vertices = np.array([
        [-half_size, -half_size, -half_size],
        [+half_size, -half_size, -half_size],
        [+half_size, +half_size, -half_size],
        [-half_size, +half_size, -half_size],
        [-half_size, -half_size, +half_size],
        [+half_size, -half_size, +half_size],
        [+half_size, +half_size, +half_size],
        [-half_size, +half_size, +half_size]
    ]) + np.array([cx, cy, cz])

    # Define the 12 triangles (2 per face)
    faces = np.array([
        [0, 3, 1], [1, 3, 2],  # bottom
        [4, 5, 7], [5, 6, 7],  # top
        [0, 1, 5], [0, 5, 4],  # front
        [2, 3, 7], [2, 7, 6],  # back
        [0, 4, 7], [0, 7, 3],  # left
        [1, 2, 6], [1, 6, 5],  # right
    ])

    # Create the mesh
    cube_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cube_mesh.vectors[i][j] = vertices[face[j]]

    return cube_mesh


def sphere(radius: float = 10.0, center: tuple[float, float, float] = (0, 0, 0),
           resolution: int = 20) -> mesh.Mesh:
    """
    Create a sphere mesh using UV sphere method.

    Args:
        radius: Radius of the sphere
        center: Center point (x, y, z)
        resolution: Number of segments (higher = smoother)

    Returns:
        mesh.Mesh: The sphere mesh
    """
    cx, cy, cz = center

    # Generate vertices
    vertices = []
    for i in range(resolution + 1):
        theta = i * np.pi / resolution
        for j in range(resolution):
            phi = j * 2 * np.pi / resolution

            x = radius * np.sin(theta) * np.cos(phi) + cx
            y = radius * np.sin(theta) * np.sin(phi) + cy
            z = radius * np.cos(theta) + cz

            vertices.append([x, y, z])

    vertices = np.array(vertices)

    # Generate faces
    faces = []
    for i in range(resolution):
        for j in range(resolution):
            # Current row vertices
            v1 = i * resolution + j
            v2 = i * resolution + (j + 1) % resolution
            # Next row vertices
            v3 = (i + 1) * resolution + j
            v4 = (i + 1) * resolution + (j + 1) % resolution

            # Two triangles per quad
            faces.append([v1, v3, v2])
            faces.append([v2, v3, v4])

    faces = np.array(faces)

    # Create the mesh
    sphere_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            sphere_mesh.vectors[i][j] = vertices[face[j]]

    return sphere_mesh


def cylinder(radius: float = 10.0, height: float = 20.0,
             center: tuple[float, float, float] = (0, 0, 0),
             resolution: int = 32) -> mesh.Mesh:
    """
    Create a cylinder mesh.

    Args:
        radius: Radius of the cylinder
        height: Height of the cylinder
        center: Center point (x, y, z)
        resolution: Number of segments around the circumference

    Returns:
        mesh.Mesh: The cylinder mesh
    """
    cx, cy, cz = center
    half_height = height / 2.0

    # Generate vertices for top and bottom circles
    vertices = []

    # Bottom circle
    for i in range(resolution):
        angle = 2 * np.pi * i / resolution
        x = radius * np.cos(angle) + cx
        y = radius * np.sin(angle) + cy
        z = -half_height + cz
        vertices.append([x, y, z])

    # Top circle
    for i in range(resolution):
        angle = 2 * np.pi * i / resolution
        x = radius * np.cos(angle) + cx
        y = radius * np.sin(angle) + cy
        z = half_height + cz
        vertices.append([x, y, z])

    # Center points for caps
    vertices.append([cx, cy, -half_height + cz])  # Bottom center
    vertices.append([cx, cy, half_height + cz])   # Top center

    vertices = np.array(vertices)

    # Generate faces
    faces = []

    # Side faces
    for i in range(resolution):
        next_i = (i + 1) % resolution
        # Bottom to top quad (2 triangles)
        faces.append([i, next_i, i + resolution])
        faces.append([next_i, next_i + resolution, i + resolution])

    # Bottom cap
    bottom_center_idx = 2 * resolution
    for i in range(resolution):
        next_i = (i + 1) % resolution
        faces.append([bottom_center_idx, next_i, i])

    # Top cap
    top_center_idx = 2 * resolution + 1
    for i in range(resolution):
        next_i = (i + 1) % resolution
        faces.append([top_center_idx, i + resolution, next_i + resolution])

    faces = np.array(faces)

    # Create the mesh
    cylinder_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cylinder_mesh.vectors[i][j] = vertices[face[j]]

    return cylinder_mesh


def cone(radius: float = 10.0, height: float = 20.0,
         center: tuple[float, float, float] = (0, 0, 0),
         resolution: int = 32) -> mesh.Mesh:
    """
    Create a cone mesh.

    Args:
        radius: Radius of the base
        height: Height of the cone
        center: Center point of the base (x, y, z)
        resolution: Number of segments around the circumference

    Returns:
        mesh.Mesh: The cone mesh
    """
    cx, cy, cz = center

    # Generate vertices
    vertices = []

    # Base circle
    for i in range(resolution):
        angle = 2 * np.pi * i / resolution
        x = radius * np.cos(angle) + cx
        y = radius * np.sin(angle) + cy
        z = cz
        vertices.append([x, y, z])

    # Apex
    vertices.append([cx, cy, cz + height])

    # Base center
    vertices.append([cx, cy, cz])

    vertices = np.array(vertices)

    # Generate faces
    faces = []
    apex_idx = resolution
    base_center_idx = resolution + 1

    # Side faces (triangles from base to apex)
    for i in range(resolution):
        next_i = (i + 1) % resolution
        faces.append([i, next_i, apex_idx])

    # Base cap
    for i in range(resolution):
        next_i = (i + 1) % resolution
        faces.append([base_center_idx, i, next_i])

    faces = np.array(faces)

    # Create the mesh
    cone_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cone_mesh.vectors[i][j] = vertices[face[j]]

    return cone_mesh


def miniature_base_28mm(center: tuple[float, float, float] = (0, 0, 0),
                        resolution: int = 32) -> mesh.Mesh:
    """
    Create a standard 28mm miniature base.

    Dimensions: 28mm diameter, 3.5mm height
    Common for tabletop wargaming miniatures (e.g., Warhammer 40k troops)

    Args:
        center: Center point of the base (x, y, z)
        resolution: Number of segments around the circumference

    Returns:
        mesh.Mesh: The 28mm base mesh
    """
    return cylinder(radius=14.0, height=3.5, center=center, resolution=resolution)


def miniature_base_32mm(center: tuple[float, float, float] = (0, 0, 0),
                        resolution: int = 32) -> mesh.Mesh:
    """
    Create a standard 32mm miniature base.

    Dimensions: 32mm diameter, 4mm height
    Common for tabletop wargaming miniatures (e.g., Warhammer 40k heroes)

    Args:
        center: Center point of the base (x, y, z)
        resolution: Number of segments around the circumference

    Returns:
        mesh.Mesh: The 32mm base mesh
    """
    return cylinder(radius=16.0, height=4.0, center=center, resolution=resolution)
