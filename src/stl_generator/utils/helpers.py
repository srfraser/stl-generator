"""Helper utilities for working with STL meshes."""

from collections import defaultdict

import numpy as np
from stl import mesh


def get_mesh_info(stl_mesh: mesh.Mesh) -> dict:
    """
    Get information about a mesh.

    Args:
        stl_mesh: The mesh to analyze

    Returns:
        dict: Dictionary containing mesh statistics
    """
    volume, cog, inertia = stl_mesh.get_mass_properties()

    min_bounds = np.min(stl_mesh.vectors.reshape(-1, 3), axis=0)
    max_bounds = np.max(stl_mesh.vectors.reshape(-1, 3), axis=0)
    dimensions = max_bounds - min_bounds

    return {
        "volume": volume,
        "center_of_gravity": cog.tolist(),
        "inertia": inertia.tolist(),
        "num_faces": len(stl_mesh.vectors),
        "min_bounds": min_bounds.tolist(),
        "max_bounds": max_bounds.tolist(),
        "dimensions": dimensions.tolist(),
    }


def is_manifold(stl_mesh: mesh.Mesh) -> tuple[bool, dict]:
    """
    Check whether a mesh is manifold (watertight and suitable for 3D printing).

    A manifold mesh has every edge shared by exactly two faces and no
    boundary or non-manifold edges.

    Args:
        stl_mesh: The mesh to check

    Returns:
        tuple[bool, dict]: (is_manifold, non_manifold_edges) where
            is_manifold is True when the mesh is fully manifold and
            non_manifold_edges maps each problematic edge to its face count.
    """
    edge_count: dict = defaultdict(int)

    for face in stl_mesh.vectors:
        # Round to 4 decimal places to handle floating-point imprecision
        v0 = tuple(round(float(x), 4) for x in face[0])
        v1 = tuple(round(float(x), 4) for x in face[1])
        v2 = tuple(round(float(x), 4) for x in face[2])

        edge_count[min(v0, v1), max(v0, v1)] += 1
        edge_count[min(v1, v2), max(v1, v2)] += 1
        edge_count[min(v2, v0), max(v2, v0)] += 1

    non_manifold_edges = {e: c for e, c in edge_count.items() if c != 2}
    return len(non_manifold_edges) == 0, non_manifold_edges


def visualize_ascii(stl_mesh: mesh.Mesh, width: int = 60, height: int = 30) -> str:
    """
    Create a simple ASCII visualization of the mesh (top-down view).

    Args:
        stl_mesh: The mesh to visualize
        width: Width of the ASCII art
        height: Height of the ASCII art

    Returns:
        str: ASCII representation of the mesh
    """
    # Get all vertices
    vertices = stl_mesh.vectors.reshape(-1, 3)

    # Project to 2D (top-down view, using X and Y)
    x_coords = vertices[:, 0]
    y_coords = vertices[:, 1]

    # Normalize to fit in the display area
    x_min, x_max = x_coords.min(), x_coords.max()
    y_min, y_max = y_coords.min(), y_coords.max()

    x_range = x_max - x_min
    y_range = y_max - y_min

    if x_range == 0 or y_range == 0:
        return "Cannot visualize: mesh has no extent in X-Y plane"

    # Create the grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Map vertices to grid
    for x, y in zip(x_coords, y_coords):
        grid_x = int((x - x_min) / x_range * (width - 1))
        grid_y = int((y - y_min) / y_range * (height - 1))
        grid[grid_y][grid_x] = '*'

    # Convert to string
    result = []
    result.append("+" + "-" * width + "+")
    for row in reversed(grid):
        result.append("|" + "".join(row) + "|")
    result.append("+" + "-" * width + "+")

    return "\n".join(result)
