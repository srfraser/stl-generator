"""Tests for primitive shapes."""

import numpy as np
from stl_generator.primitives import (
    cube,
    sphere,
    cylinder,
    cone,
    miniature_base_28mm,
    miniature_base_32mm,
)


def test_cube_creation():
    """Test cube creation."""
    mesh = cube(size=10)
    assert mesh is not None
    assert len(mesh.vectors) == 12  # 12 triangles (2 per face, 6 faces)


def test_sphere_creation():
    """Test sphere creation."""
    mesh = sphere(radius=10, resolution=20)
    assert mesh is not None
    assert len(mesh.vectors) > 0


def test_cylinder_creation():
    """Test cylinder creation."""
    mesh = cylinder(radius=10, height=20, resolution=32)
    assert mesh is not None
    assert len(mesh.vectors) > 0


def test_cone_creation():
    """Test cone creation."""
    mesh = cone(radius=10, height=20, resolution=32)
    assert mesh is not None
    assert len(mesh.vectors) > 0


def test_cube_with_center():
    """Test cube creation with custom center."""
    mesh = cube(size=10, center=(5, 5, 5))
    assert mesh is not None
    # Check that vertices are offset (cube centered at (5,5,5) with size 10
    # should have min coords at (0,0,0) and max at (10,10,10))
    min_coords = np.min(mesh.vectors.reshape(-1, 3), axis=0)
    max_coords = np.max(mesh.vectors.reshape(-1, 3), axis=0)
    assert np.allclose(min_coords, [0, 0, 0])
    assert np.allclose(max_coords, [10, 10, 10])


def test_miniature_base_28mm():
    """Test 28mm miniature base creation."""
    mesh = miniature_base_28mm()
    assert mesh is not None
    assert len(mesh.vectors) > 0

    # Check dimensions: 28mm diameter = 14mm radius, 3.5mm height
    vertices = mesh.vectors.reshape(-1, 3)

    # Check height (Z dimension)
    z_min = vertices[:, 2].min()
    z_max = vertices[:, 2].max()
    height = z_max - z_min
    assert np.isclose(height, 3.5, atol=0.01)

    # Check radius (XY plane)
    xy_distances = np.sqrt(vertices[:, 0]**2 + vertices[:, 1]**2)
    max_radius = xy_distances.max()
    assert np.isclose(max_radius, 14.0, atol=0.1)


def test_miniature_base_32mm():
    """Test 32mm miniature base creation."""
    mesh = miniature_base_32mm()
    assert mesh is not None
    assert len(mesh.vectors) > 0

    # Check dimensions: 32mm diameter = 16mm radius, 4mm height
    vertices = mesh.vectors.reshape(-1, 3)

    # Check height (Z dimension)
    z_min = vertices[:, 2].min()
    z_max = vertices[:, 2].max()
    height = z_max - z_min
    assert np.isclose(height, 4.0, atol=0.01)

    # Check radius (XY plane)
    xy_distances = np.sqrt(vertices[:, 0]**2 + vertices[:, 1]**2)
    max_radius = xy_distances.max()
    assert np.isclose(max_radius, 16.0, atol=0.1)


def test_miniature_base_with_offset():
    """Test miniature base with custom center."""
    mesh = miniature_base_28mm(center=(10, 20, 5))
    assert mesh is not None

    vertices = mesh.vectors.reshape(-1, 3)

    # Check that center is offset
    x_center = (vertices[:, 0].min() + vertices[:, 0].max()) / 2
    y_center = (vertices[:, 1].min() + vertices[:, 1].max()) / 2

    assert np.isclose(x_center, 10.0, atol=0.1)
    assert np.isclose(y_center, 20.0, atol=0.1)


if __name__ == "__main__":
    test_cube_creation()
    test_sphere_creation()
    test_cylinder_creation()
    test_cone_creation()
    test_cube_with_center()
    test_miniature_base_28mm()
    test_miniature_base_32mm()
    test_miniature_base_with_offset()
    print("All tests passed!")
