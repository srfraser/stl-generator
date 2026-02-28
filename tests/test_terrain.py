"""Tests for terrain pieces for 32mm fantasy dioramas."""

import numpy as np
from stl_generator.terrain import (
    dungeon_floor_tile,
    dungeon_wall_section,
    cobblestone_street_tile,
)
from stl_generator.primitives import box


# ---------------------------------------------------------------------------
# box() primitive tests
# ---------------------------------------------------------------------------

def test_box_creation():
    """Test that box() returns a valid mesh."""
    m = box(width=20.0, depth=10.0, height=5.0)
    assert m is not None
    assert len(m.vectors) == 12  # 12 triangles (2 per face, 6 faces)


def test_box_dimensions():
    """Test that box dimensions are correct."""
    m = box(width=20.0, depth=10.0, height=5.0)
    verts = m.vectors.reshape(-1, 3)
    x_range = verts[:, 0].max() - verts[:, 0].min()
    y_range = verts[:, 1].max() - verts[:, 1].min()
    z_range = verts[:, 2].max() - verts[:, 2].min()
    assert np.isclose(x_range, 20.0, atol=0.01)
    assert np.isclose(y_range, 10.0, atol=0.01)
    assert np.isclose(z_range, 5.0, atol=0.01)


def test_box_center():
    """Test that box center offset is applied correctly."""
    m = box(width=10.0, depth=10.0, height=10.0, center=(5.0, 5.0, 5.0))
    verts = m.vectors.reshape(-1, 3)
    assert np.isclose(verts[:, 0].min(), 0.0, atol=0.01)
    assert np.isclose(verts[:, 0].max(), 10.0, atol=0.01)


# ---------------------------------------------------------------------------
# dungeon_floor_tile tests
# ---------------------------------------------------------------------------

def test_dungeon_floor_tile_default():
    """Test default dungeon floor tile (50×50mm)."""
    m = dungeon_floor_tile()
    assert m is not None
    assert len(m.vectors) > 12  # More than a plain box


def test_dungeon_floor_tile_dimensions():
    """Test that floor tile footprint stays within the declared width/depth."""
    w, d, t = 50.0, 50.0, 5.0
    m = dungeon_floor_tile(width=w, depth=d, thickness=t)
    verts = m.vectors.reshape(-1, 3)
    # XY footprint should not exceed declared dimensions
    assert verts[:, 0].max() <= w / 2 + 0.01
    assert verts[:, 0].min() >= -w / 2 - 0.01
    assert verts[:, 1].max() <= d / 2 + 0.01
    assert verts[:, 1].min() >= -d / 2 - 0.01
    # Base thickness check
    z_range = verts[:, 2].max() - verts[:, 2].min()
    assert z_range >= t  # At least the base thickness


def test_dungeon_floor_tile_stone_height():
    """Test that stones protrude above the base surface."""
    t = 5.0
    sh = 0.5
    m = dungeon_floor_tile(thickness=t, stone_height=sh)
    verts = m.vectors.reshape(-1, 3)
    total_height = verts[:, 2].max() - verts[:, 2].min()
    assert total_height > t
    assert total_height <= t + sh + 0.1


def test_dungeon_floor_tile_custom_size():
    """Test floor tile with custom dimensions (e.g., 100×50mm)."""
    m = dungeon_floor_tile(width=100.0, depth=50.0, thickness=4.0, stone_size=12.0)
    assert m is not None
    assert len(m.vectors) > 12


# ---------------------------------------------------------------------------
# dungeon_wall_section tests
# ---------------------------------------------------------------------------

def test_dungeon_wall_section_default():
    """Test default dungeon wall section (50×40×8mm)."""
    m = dungeon_wall_section()
    assert m is not None
    assert len(m.vectors) > 12


def test_dungeon_wall_section_dimensions():
    """Test that wall section footprint stays within declared dimensions."""
    w, h, t = 50.0, 40.0, 8.0
    m = dungeon_wall_section(width=w, height=h, thickness=t)
    verts = m.vectors.reshape(-1, 3)
    x_range = verts[:, 0].max() - verts[:, 0].min()
    z_range = verts[:, 2].max() - verts[:, 2].min()
    assert np.isclose(x_range, w, atol=0.01)
    assert np.isclose(z_range, h, atol=0.01)


def test_dungeon_wall_section_relief():
    """Test that stone relief protrudes from wall face."""
    t = 8.0
    relief = 0.5
    m = dungeon_wall_section(thickness=t, relief=relief)
    verts = m.vectors.reshape(-1, 3)
    y_range = verts[:, 1].max() - verts[:, 1].min()
    # Depth should be wall thickness + relief (stones protrude from front face)
    assert y_range > t
    assert y_range <= t + relief + 0.1


def test_dungeon_wall_section_custom():
    """Test wall with custom course/stone dimensions."""
    m = dungeon_wall_section(
        width=80.0, height=30.0, thickness=10.0,
        course_height=6.0, stone_length=12.0,
    )
    assert m is not None
    assert len(m.vectors) > 12


# ---------------------------------------------------------------------------
# cobblestone_street_tile tests
# ---------------------------------------------------------------------------

def test_cobblestone_street_tile_default():
    """Test default cobblestone street tile (50×50mm)."""
    m = cobblestone_street_tile()
    assert m is not None
    assert len(m.vectors) > 12


def test_cobblestone_street_tile_dimensions():
    """Test that cobblestone tile stays within declared footprint."""
    w, d, t = 50.0, 50.0, 5.0
    m = cobblestone_street_tile(width=w, depth=d, thickness=t)
    verts = m.vectors.reshape(-1, 3)
    assert verts[:, 0].max() <= w / 2 + 0.01
    assert verts[:, 0].min() >= -w / 2 - 0.01
    assert verts[:, 1].max() <= d / 2 + 0.01
    assert verts[:, 1].min() >= -d / 2 - 0.01


def test_cobblestone_street_tile_height():
    """Test that cobblestones protrude above the base surface."""
    t = 5.0
    sh = 0.5
    m = cobblestone_street_tile(thickness=t, stone_height=sh)
    verts = m.vectors.reshape(-1, 3)
    total_height = verts[:, 2].max() - verts[:, 2].min()
    assert total_height > t
    assert total_height <= t + sh + 0.1


def test_cobblestone_street_tile_custom():
    """Test cobblestone tile with custom dimensions."""
    m = cobblestone_street_tile(width=75.0, depth=50.0, stone_size=8.0, gap=0.8)
    assert m is not None
    assert len(m.vectors) > 12


if __name__ == "__main__":
    test_box_creation()
    test_box_dimensions()
    test_box_center()
    test_dungeon_floor_tile_default()
    test_dungeon_floor_tile_dimensions()
    test_dungeon_floor_tile_stone_height()
    test_dungeon_floor_tile_custom_size()
    test_dungeon_wall_section_default()
    test_dungeon_wall_section_dimensions()
    test_dungeon_wall_section_relief()
    test_dungeon_wall_section_custom()
    test_cobblestone_street_tile_default()
    test_cobblestone_street_tile_dimensions()
    test_cobblestone_street_tile_height()
    test_cobblestone_street_tile_custom()
    print("All terrain tests passed!")
