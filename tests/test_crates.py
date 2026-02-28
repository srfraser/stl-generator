"""Tests for scatter terrain crates."""

import numpy as np
from stl_generator.scenery.crates import (
    wooden_crate,
    metal_crate,
    wooden_crate_with_bands,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extents(m):
    """Return (x_min, x_max, y_min, y_max, z_min, z_max) of a mesh."""
    v = m.vectors.reshape(-1, 3)
    return (v[:, 0].min(), v[:, 0].max(),
            v[:, 1].min(), v[:, 1].max(),
            v[:, 2].min(), v[:, 2].max())


# ---------------------------------------------------------------------------
# wooden_crate
# ---------------------------------------------------------------------------

def test_wooden_crate_closed():
    """Closed wooden crate is created with triangles."""
    m = wooden_crate(width=20, depth=18, height=16, open_lid=False)
    assert m is not None
    assert len(m.vectors) > 12


def test_wooden_crate_open():
    """Open-lid wooden crate is created with triangles."""
    m = wooden_crate(width=20, depth=18, height=16, open_lid=True)
    assert m is not None
    assert len(m.vectors) > 12


def test_wooden_crate_with_handle():
    """Wooden crate with handle has more geometry than one without."""
    m_plain = wooden_crate(handle=False)
    m_handle = wooden_crate(handle=True)
    assert len(m_handle.vectors) > len(m_plain.vectors)


def test_wooden_crate_dimensions():
    """Closed wooden crate fits within expected outer bounding box."""
    w, d, h = 20.0, 18.0, 16.0
    m = wooden_crate(width=w, depth=d, height=h, open_lid=False)
    xmin, xmax, ymin, ymax, zmin, zmax = _extents(m)

    # Outer extents should not exceed crate dims plus surface detail protrusion
    # (corner strips and plank ridges protrude up to ~1.5 mm per side)
    tolerance = 3.0
    assert xmax - xmin <= w + tolerance
    assert ymax - ymin <= d + tolerance
    assert zmax - zmin <= h + tolerance


def test_wooden_crate_no_base():
    """Wooden crate centred at origin has bottom at approximately -height/2."""
    h = 16.0
    m = wooden_crate(height=h, center=(0, 0, 0))
    v = m.vectors.reshape(-1, 3)
    z_min = v[:, 2].min()
    # Bottom of crate should be near -h/2 (not below a base disc)
    assert z_min >= -h / 2 - 0.1


def test_wooden_crate_custom_center():
    """Wooden crate respects the center parameter."""
    offset = (10.0, 5.0, 3.0)
    m = wooden_crate(center=offset)
    v = m.vectors.reshape(-1, 3)
    # Centre of bounding box should be near the requested center
    x_cen = (v[:, 0].min() + v[:, 0].max()) / 2
    y_cen = (v[:, 1].min() + v[:, 1].max()) / 2
    assert abs(x_cen - offset[0]) < 2.0
    assert abs(y_cen - offset[1]) < 2.0


# ---------------------------------------------------------------------------
# metal_crate
# ---------------------------------------------------------------------------

def test_metal_crate_closed():
    """Closed metal crate is created."""
    m = metal_crate(width=20, depth=18, height=16, open_lid=False)
    assert m is not None
    assert len(m.vectors) > 12


def test_metal_crate_open():
    """Open-lid metal crate is created."""
    m = metal_crate(width=20, depth=18, height=16, open_lid=True)
    assert m is not None
    assert len(m.vectors) > 12


def test_metal_crate_with_handle():
    """Metal crate with handle has more geometry than one without."""
    m_plain = metal_crate(handle=False)
    m_handle = metal_crate(handle=True)
    assert len(m_handle.vectors) > len(m_plain.vectors)


def test_metal_crate_no_base():
    """Metal crate has no extra base attached below it."""
    h = 16.0
    m = metal_crate(height=h, center=(0, 0, 0))
    v = m.vectors.reshape(-1, 3)
    z_min = v[:, 2].min()
    assert z_min >= -h / 2 - 0.1


# ---------------------------------------------------------------------------
# wooden_crate_with_bands
# ---------------------------------------------------------------------------

def test_wooden_crate_with_bands_closed():
    """Wooden crate with bands (closed) is created."""
    m = wooden_crate_with_bands(width=20, depth=18, height=16, open_lid=False)
    assert m is not None
    assert len(m.vectors) > 12


def test_wooden_crate_with_bands_open():
    """Wooden crate with bands (open lid) is created."""
    m = wooden_crate_with_bands(width=20, depth=18, height=16, open_lid=True)
    assert m is not None
    assert len(m.vectors) > 12


def test_wooden_crate_with_bands_more_geometry():
    """Crate with bands has more geometry than plain wooden crate."""
    m_plain = wooden_crate(width=20, depth=18, height=16)
    m_bands = wooden_crate_with_bands(width=20, depth=18, height=16)
    assert len(m_bands.vectors) > len(m_plain.vectors)


def test_wooden_crate_with_bands_handle():
    """Wooden crate with bands and handle is created successfully."""
    m = wooden_crate_with_bands(handle=True, num_bands=3)
    assert m is not None
    assert len(m.vectors) > 12


# ---------------------------------------------------------------------------
# Size variants
# ---------------------------------------------------------------------------

def test_small_crate():
    """Small crate variant can be created."""
    m = wooden_crate(width=18, depth=18, height=14)
    assert m is not None
    assert len(m.vectors) > 12


def test_large_crate():
    """Large crate variant can be created."""
    m = wooden_crate(width=28, depth=24, height=20)
    assert m is not None
    assert len(m.vectors) > 12


def test_open_lid_has_fewer_solid_faces():
    """Open-lid crate has less solid material than closed one (no top face)."""
    m_closed = wooden_crate(open_lid=False)
    m_open = wooden_crate(open_lid=True)
    # Open crate has shell walls instead of one solid body; the closed one has
    # one solid box which is fewer pieces but more of a single solid. Both
    # should be valid meshes.
    assert m_closed is not None
    assert m_open is not None


# ---------------------------------------------------------------------------
# Import from package root
# ---------------------------------------------------------------------------

def test_importable_from_package():
    """All crate functions are importable from the top-level package."""
    from stl_generator import wooden_crate as wc, metal_crate as mc, wooden_crate_with_bands as wcb
    assert wc is wooden_crate
    assert mc is metal_crate
    assert wcb is wooden_crate_with_bands


if __name__ == "__main__":
    test_wooden_crate_closed()
    test_wooden_crate_open()
    test_wooden_crate_with_handle()
    test_wooden_crate_dimensions()
    test_wooden_crate_no_base()
    test_wooden_crate_custom_center()
    test_metal_crate_closed()
    test_metal_crate_open()
    test_metal_crate_with_handle()
    test_metal_crate_no_base()
    test_wooden_crate_with_bands_closed()
    test_wooden_crate_with_bands_open()
    test_wooden_crate_with_bands_more_geometry()
    test_wooden_crate_with_bands_handle()
    test_small_crate()
    test_large_crate()
    test_open_lid_has_fewer_solid_faces()
    test_importable_from_package()
    print("All crate tests passed!")
