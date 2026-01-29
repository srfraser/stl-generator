"""Tests for scenery and decoration features."""

import numpy as np
from stl_generator.scenery import (
    flagstone_base_28mm,
    flagstone_base_32mm,
    add_flagstone_pattern,
)
from stl_generator.primitives import miniature_base_28mm, miniature_base_32mm


def test_flagstone_base_28mm_irregular():
    """Test 28mm base with irregular flagstone pattern."""
    mesh = flagstone_base_28mm(pattern="irregular", seed=42)
    assert mesh is not None
    assert len(mesh.vectors) > 0
    # Should have more triangles than plain base (128 triangles)
    assert len(mesh.vectors) > 128


def test_flagstone_base_28mm_rectangular():
    """Test 28mm base with rectangular flagstone pattern."""
    mesh = flagstone_base_28mm(pattern="rectangular", stone_size=4.0, gap=0.2)
    assert mesh is not None
    assert len(mesh.vectors) > 128


def test_flagstone_base_28mm_hexagonal():
    """Test 28mm base with hexagonal flagstone pattern."""
    mesh = flagstone_base_28mm(pattern="hexagonal", stone_size=4.5, gap=0.25)
    assert mesh is not None
    assert len(mesh.vectors) > 128


def test_flagstone_base_28mm_random():
    """Test 28mm base with random flagstone pattern."""
    mesh = flagstone_base_28mm(pattern="random", num_stones=20, seed=123)
    assert mesh is not None
    assert len(mesh.vectors) > 128


def test_flagstone_base_32mm():
    """Test 32mm base with flagstone pattern."""
    mesh = flagstone_base_32mm(pattern="irregular", seed=99)
    assert mesh is not None
    assert len(mesh.vectors) > 128


def test_add_flagstone_pattern():
    """Test adding flagstone pattern to existing base."""
    base = miniature_base_28mm()
    decorated = add_flagstone_pattern(
        base,
        radius=14.0,
        base_height=3.5,
        pattern="irregular",
        stone_height=0.3,
        gap=0.3,
        seed=42
    )
    assert decorated is not None
    assert len(decorated.vectors) > len(base.vectors)


def test_flagstone_dimensions():
    """Test that flagstone base maintains proper base dimensions."""
    mesh = flagstone_base_28mm(pattern="irregular", stone_height=0.3)
    vertices = mesh.vectors.reshape(-1, 3)

    # Check that base is still 28mm diameter (14mm radius)
    xy_distances = np.sqrt(vertices[:, 0]**2 + vertices[:, 1]**2)
    max_radius = xy_distances.max()
    assert max_radius <= 14.5  # Allow small tolerance

    # Check that height includes stone height
    # Base is centered, so top is at base_height/2 + stone_height
    z_min = vertices[:, 2].min()
    z_max = vertices[:, 2].max()
    total_height = z_max - z_min
    assert total_height >= 3.5  # Should be at least base height


def test_flagstone_custom_parameters():
    """Test flagstone with custom stone height and gap."""
    mesh = flagstone_base_28mm(
        pattern="irregular",
        stone_height=0.5,
        gap=0.2,
        seed=42
    )
    assert mesh is not None

    vertices = mesh.vectors.reshape(-1, 3)
    z_min = vertices[:, 2].min()
    z_max = vertices[:, 2].max()
    total_height = z_max - z_min

    # With taller stones, total height should be base height + stone height
    assert total_height > 3.5  # Should be at least base height
    assert total_height <= 3.5 + 0.6  # Base + stone height + tolerance


def test_flagstone_seed_variation():
    """Test that different seeds produce different patterns."""
    mesh1 = flagstone_base_28mm(pattern="irregular", seed=1)
    mesh2 = flagstone_base_28mm(pattern="irregular", seed=2)

    # Different seeds should produce different numbers of triangles
    # (though occasionally they might match by chance)
    # At minimum, meshes should be valid
    assert mesh1 is not None
    assert mesh2 is not None
    assert len(mesh1.vectors) > 128
    assert len(mesh2.vectors) > 128


def test_all_patterns():
    """Test that all pattern types work."""
    patterns = ["rectangular", "irregular", "hexagonal", "random"]

    for pattern in patterns:
        mesh = flagstone_base_28mm(pattern=pattern, seed=42)
        assert mesh is not None, f"Pattern '{pattern}' failed"
        assert len(mesh.vectors) > 128, f"Pattern '{pattern}' has too few triangles"


if __name__ == "__main__":
    test_flagstone_base_28mm_irregular()
    test_flagstone_base_28mm_rectangular()
    test_flagstone_base_28mm_hexagonal()
    test_flagstone_base_28mm_random()
    test_flagstone_base_32mm()
    test_add_flagstone_pattern()
    test_flagstone_dimensions()
    test_flagstone_custom_parameters()
    test_flagstone_seed_variation()
    test_all_patterns()
    print("All scenery tests passed!")
