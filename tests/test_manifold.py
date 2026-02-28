"""Tests verifying that generated STL meshes are manifold (watertight).

A manifold mesh has every edge shared by exactly two faces, making it
suitable for 3D printing.
"""

import pytest
from stl_generator.primitives import (
    cube,
    cylinder,
    cone,
    miniature_base_28mm,
    miniature_base_32mm,
)
from stl_generator.scenery import (
    flagstone_base_28mm,
    flagstone_base_32mm,
)
from stl_generator.utils import is_manifold


def assert_manifold(mesh, name: str) -> None:
    """Assert that a mesh is manifold, printing non-manifold edges on failure."""
    manifold, bad_edges = is_manifold(mesh)
    assert manifold, (
        f"{name} is not manifold: {len(bad_edges)} non-manifold edge(s) found"
    )


def test_cube_is_manifold():
    assert_manifold(cube(size=10), "cube")


def test_cylinder_is_manifold():
    assert_manifold(cylinder(radius=10, height=20, resolution=32), "cylinder")


def test_cone_is_manifold():
    assert_manifold(cone(radius=10, height=20, resolution=32), "cone")


def test_miniature_base_28mm_is_manifold():
    assert_manifold(miniature_base_28mm(), "miniature_base_28mm")


def test_miniature_base_32mm_is_manifold():
    assert_manifold(miniature_base_32mm(), "miniature_base_32mm")


@pytest.mark.parametrize("pattern", ["rectangular", "irregular", "hexagonal", "random"])
def test_flagstone_base_28mm_is_manifold(pattern):
    mesh = flagstone_base_28mm(pattern=pattern, seed=42)
    assert_manifold(mesh, f"flagstone_base_28mm(pattern={pattern!r})")


@pytest.mark.parametrize("pattern", ["rectangular", "irregular", "hexagonal", "random"])
def test_flagstone_base_32mm_is_manifold(pattern):
    mesh = flagstone_base_32mm(pattern=pattern, seed=42)
    assert_manifold(mesh, f"flagstone_base_32mm(pattern={pattern!r})")
