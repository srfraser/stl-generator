"""Scatter terrain crates scaled for 32mm miniatures.

Provides wooden and metal crates with optional open lids, handles,
and wooden crates with decorative metal bands. All crates have no
attached miniature base and are sized appropriately for 32mm scale.
"""

import numpy as np
from stl import mesh
from stl_generator.generators import BaseGenerator


# Default wall thickness for open-lid crates (mm)
_WALL_THICKNESS = 1.5


def _solid_box(cx: float, cy: float, cz: float,
               width: float, depth: float, height: float) -> mesh.Mesh:
    """Create a solid rectangular box mesh centered at (cx, cy, cz).

    Args:
        cx, cy, cz: Centre coordinates
        width: Dimension along X axis
        depth: Dimension along Y axis
        height: Dimension along Z axis

    Returns:
        mesh.Mesh: The box mesh
    """
    hw, hd, hh = width / 2, depth / 2, height / 2

    vertices = np.array([
        [cx - hw, cy - hd, cz - hh],  # 0 bottom-front-left
        [cx + hw, cy - hd, cz - hh],  # 1 bottom-front-right
        [cx + hw, cy + hd, cz - hh],  # 2 bottom-back-right
        [cx - hw, cy + hd, cz - hh],  # 3 bottom-back-left
        [cx - hw, cy - hd, cz + hh],  # 4 top-front-left
        [cx + hw, cy - hd, cz + hh],  # 5 top-front-right
        [cx + hw, cy + hd, cz + hh],  # 6 top-back-right
        [cx - hw, cy + hd, cz + hh],  # 7 top-back-left
    ])

    faces = np.array([
        [0, 3, 1], [1, 3, 2],  # bottom
        [4, 5, 7], [5, 6, 7],  # top
        [0, 1, 5], [0, 5, 4],  # front (-y)
        [2, 3, 7], [2, 7, 6],  # back (+y)
        [0, 4, 7], [0, 7, 3],  # left (-x)
        [1, 2, 6], [1, 6, 5],  # right (+x)
    ])

    box_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            box_mesh.vectors[i][j] = vertices[face[j]]

    return box_mesh


def _open_box_shell(cx: float, cy: float, cz: float,
                    width: float, depth: float, height: float,
                    wall: float = _WALL_THICKNESS) -> list:
    """Return a list of meshes forming an open-top box shell (4 walls + bottom).

    Args:
        cx, cy, cz: Centre coordinates (centre of the outer extents)
        width: Outer dimension along X axis
        depth: Outer dimension along Y axis
        height: Outer dimension along Z axis
        wall: Wall thickness

    Returns:
        list[mesh.Mesh]: Component meshes of the shell
    """
    hw, hd, hh = width / 2, depth / 2, height / 2

    # Bottom panel (full width/depth, wall_thickness thick)
    bottom_cz = cz - hh + wall / 2
    bottom = _solid_box(cx, cy, bottom_cz, width, depth, wall)

    # Front wall (-y face): full width, wall thick in y, from bottom to top
    inner_height = height - wall  # height above the bottom panel
    side_cz = cz - hh + wall + inner_height / 2
    front = _solid_box(cx, cy - hd + wall / 2, side_cz, width, wall, inner_height)
    back = _solid_box(cx, cy + hd - wall / 2, side_cz, width, wall, inner_height)

    # Left/right walls fit between front/back walls
    inner_depth = depth - 2 * wall
    left = _solid_box(cx - hw + wall / 2, cy, side_cz, wall, inner_depth, inner_height)
    right = _solid_box(cx + hw - wall / 2, cy, side_cz, wall, inner_depth, inner_height)

    return [bottom, front, back, left, right]


def _plank_detail(cx: float, cy: float, cz: float,
                  width: float, depth: float, height: float,
                  plank_spacing: float = 3.5,
                  ridge_height: float = 0.5,
                  ridge_width: float = 0.8) -> list:
    """Return raised plank-line ridges on all four sides of a box.

    Ridges run horizontally at evenly-spaced intervals to represent
    the gaps between wooden planks.

    Args:
        cx, cy, cz: Centre of the crate body
        width: Crate width (X)
        depth: Crate depth (Y)
        height: Crate height (Z)
        plank_spacing: Approximate distance between ridge centres (mm)
        ridge_height: How far ridges protrude from the face (mm)
        ridge_width: Height (in Z) of each ridge strip (mm)

    Returns:
        list[mesh.Mesh]: Ridge meshes
    """
    ridges = []
    hw, hd, hh = width / 2, depth / 2, height / 2

    # Compute z positions for ridges (excluding very top and bottom)
    bottom_z = cz - hh
    num_ridges = max(1, int(height / plank_spacing) - 1)
    step = height / (num_ridges + 1)

    z_positions = [bottom_z + step * (i + 1) for i in range(num_ridges)]

    for z in z_positions:
        # Front face (-y): ridge protrudes in -y direction
        ridges.append(_solid_box(
            cx, cy - hd - ridge_height / 2, z,
            width, ridge_height, ridge_width
        ))
        # Back face (+y): ridge protrudes in +y direction
        ridges.append(_solid_box(
            cx, cy + hd + ridge_height / 2, z,
            width, ridge_height, ridge_width
        ))
        # Left face (-x): ridge protrudes in -x direction
        ridges.append(_solid_box(
            cx - hw - ridge_height / 2, cy, z,
            ridge_height, depth, ridge_width
        ))
        # Right face (+x): ridge protrudes in +x direction
        ridges.append(_solid_box(
            cx + hw + ridge_height / 2, cy, z,
            ridge_height, depth, ridge_width
        ))

    return ridges


def _corner_strip_detail(cx: float, cy: float, cz: float,
                         width: float, depth: float, height: float,
                         strip_width: float = 1.5,
                         strip_protrude: float = 0.4) -> list:
    """Return vertical corner reinforcement strips on all four corners.

    Args:
        cx, cy, cz: Centre of the crate body
        width: Crate width (X)
        depth: Crate depth (Y)
        height: Crate height (Z)
        strip_width: Width of each corner strip (mm)
        strip_protrude: How far the strip protrudes from the face (mm)

    Returns:
        list[mesh.Mesh]: Corner strip meshes
    """
    strips = []
    hw, hd = width / 2, depth / 2
    # 4 vertical corners
    corners = [
        (cx - hw - strip_protrude / 2, cy - hd - strip_protrude / 2),
        (cx + hw + strip_protrude / 2, cy - hd - strip_protrude / 2),
        (cx + hw + strip_protrude / 2, cy + hd + strip_protrude / 2),
        (cx - hw - strip_protrude / 2, cy + hd + strip_protrude / 2),
    ]
    corner_w = strip_width + strip_protrude
    for corner_cx, corner_cy in corners:
        strips.append(_solid_box(corner_cx, corner_cy, cz,
                                 corner_w, corner_w, height))
    return strips


def _metal_band_detail(cx: float, cy: float, cz: float,
                       width: float, depth: float, height: float,
                       num_bands: int = 2,
                       band_height: float = 2.5,
                       band_protrude: float = 0.6) -> list:
    """Return metal band meshes wrapping all four sides of a box.

    Args:
        cx, cy, cz: Centre of the crate body
        width: Crate width (X)
        depth: Crate depth (Y)
        height: Crate height (Z)
        num_bands: Number of bands
        band_height: Height of each band in Z (mm)
        band_protrude: How far each band protrudes from the face (mm)

    Returns:
        list[mesh.Mesh]: Band meshes
    """
    bands = []
    hw, hd, hh = width / 2, depth / 2, height / 2
    bottom_z = cz - hh

    step = height / (num_bands + 1)
    z_positions = [bottom_z + step * (i + 1) for i in range(num_bands)]

    band_w = width + 2 * band_protrude
    band_d = depth + 2 * band_protrude

    for z in z_positions:
        # Front band
        bands.append(_solid_box(cx, cy - hd - band_protrude / 2, z,
                                band_w, band_protrude, band_height))
        # Back band
        bands.append(_solid_box(cx, cy + hd + band_protrude / 2, z,
                                band_w, band_protrude, band_height))
        # Left band
        bands.append(_solid_box(cx - hw - band_protrude / 2, cy, z,
                                band_protrude, band_d, band_height))
        # Right band
        bands.append(_solid_box(cx + hw + band_protrude / 2, cy, z,
                                band_protrude, band_d, band_height))

    return bands


def _lid_rim(cx: float, cy: float, cz: float,
             width: float, depth: float,
             rim_height: float = 2.0,
             rim_thickness: float = 1.5) -> list:
    """Return a rectangular rim frame for an open-lid crate.

    The rim sits on top of the crate walls and visually defines the
    opening.

    Args:
        cx, cy, cz: Centre of the crate body
        width: Crate outer width (X)
        depth: Crate outer depth (Y)
        rim_height: Height of the rim frame (mm)
        rim_thickness: Thickness of each rim strip (mm)

    Returns:
        list[mesh.Mesh]: Rim strip meshes
    """
    hw, hd, hh = width / 2, depth / 2, 0.0  # cz is already top centre
    rim_cz = cz + rim_height / 2

    inner_depth = depth - 2 * rim_thickness

    front = _solid_box(cx, cy - hd + rim_thickness / 2, rim_cz,
                       width, rim_thickness, rim_height)
    back = _solid_box(cx, cy + hd - rim_thickness / 2, rim_cz,
                      width, rim_thickness, rim_height)
    left = _solid_box(cx - hw + rim_thickness / 2, cy, rim_cz,
                      rim_thickness, inner_depth, rim_height)
    right = _solid_box(cx + hw - rim_thickness / 2, cy, rim_cz,
                       rim_thickness, inner_depth, rim_height)

    return [front, back, left, right]


def _handle(cx: float, cy: float, cz: float,
            crate_width: float,
            post_width: float = 1.5,
            post_height: float = 3.0,
            bar_width: float = 6.0,
            protrude: float = 2.5) -> list:
    """Return a D-ring handle protruding from the +y face of a crate.

    The handle consists of two upright posts and a horizontal bar
    spanning between them.

    Args:
        cx, cy, cz: Centre of the crate body face (on the +y face)
        crate_width: Width of the crate (used to position posts)
        post_width: Cross-section width of each post (mm)
        post_height: Height of each post (mm)
        bar_width: Distance between post centres (mm)
        protrude: How far the handle stands off from the face (mm)

    Returns:
        list[mesh.Mesh]: Handle component meshes
    """
    parts = []
    bar_w = min(bar_width, crate_width * 0.5)
    bar_half = bar_w / 2

    # Posts rise from cz upward
    post_bottom_cz = cz + post_height / 2
    left_post = _solid_box(cx - bar_half, cy + protrude / 2, post_bottom_cz,
                           post_width, protrude, post_height)
    right_post = _solid_box(cx + bar_half, cy + protrude / 2, post_bottom_cz,
                            post_width, protrude, post_height)

    # Horizontal bar across the top of the posts
    bar_cz = cz + post_height + post_width / 2
    bar_depth = protrude + post_width
    bar = _solid_box(cx, cy + bar_depth / 2 - post_width / 2, bar_cz,
                     bar_w + post_width, post_width, post_width)

    parts.extend([left_post, right_post, bar])
    return parts


def wooden_crate(
    width: float = 20.0,
    depth: float = 18.0,
    height: float = 16.0,
    open_lid: bool = False,
    handle: bool = False,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> mesh.Mesh:
    """Create a wooden scatter terrain crate for 32mm miniatures.

    The crate has horizontal plank-line ridges and vertical corner
    reinforcements. No miniature base is attached.

    Args:
        width: Outer width in mm (X axis). Default 20 mm.
        depth: Outer depth in mm (Y axis). Default 18 mm.
        height: Outer height in mm (Z axis). Default 16 mm.
        open_lid: If True, the crate has an open top showing the
            interior; if False, the crate has a solid closed lid.
        handle: If True, add a D-ring handle on the front and back faces.
        center: (x, y, z) centre of the crate. Default (0, 0, 0).

    Returns:
        mesh.Mesh: The crate mesh
    """
    cx, cy, cz = center
    gen = BaseGenerator()

    if open_lid:
        for part in _open_box_shell(cx, cy, cz, width, depth, height):
            gen.add_mesh(part)
        # Lid rim to define the opening
        top_cz = cz + height / 2 - _WALL_THICKNESS
        for part in _lid_rim(cx, cy, top_cz, width, depth,
                             rim_height=1.5, rim_thickness=1.5):
            gen.add_mesh(part)
    else:
        gen.add_mesh(_solid_box(cx, cy, cz, width, depth, height))

    # Plank line ridges on all four sides
    for ridge in _plank_detail(cx, cy, cz, width, depth, height):
        gen.add_mesh(ridge)

    # Vertical corner strips
    for strip in _corner_strip_detail(cx, cy, cz, width, depth, height):
        gen.add_mesh(strip)

    if handle:
        hh = height / 2
        hd = depth / 2
        # Handles on front and back faces (centred in z at 60 % of height)
        handle_cz = cz - hh + height * 0.6
        for part in _handle(cx, cy - hd, handle_cz, width):
            gen.add_mesh(part)
        # Rotate the back handle by 180° about Z (flip it to face +y)
        for part in _handle(cx, cy + hd, handle_cz, width):
            # Mirror y offset: flip the protrude direction
            part.vectors[:, :, 1] = 2 * (cy + hd) - part.vectors[:, :, 1]
            gen.add_mesh(part)

    return gen.combine()


def metal_crate(
    width: float = 20.0,
    depth: float = 18.0,
    height: float = 16.0,
    open_lid: bool = False,
    handle: bool = False,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> mesh.Mesh:
    """Create a metal scatter terrain crate for 32mm miniatures.

    The crate has a clean surface with a raised border frame around
    each face to simulate sheet-metal construction. No miniature base
    is attached.

    Args:
        width: Outer width in mm (X axis). Default 20 mm.
        depth: Outer depth in mm (Y axis). Default 18 mm.
        height: Outer height in mm (Z axis). Default 16 mm.
        open_lid: If True, the crate has an open top; if False, closed lid.
        handle: If True, add a D-ring handle on the front and back faces.
        center: (x, y, z) centre of the crate. Default (0, 0, 0).

    Returns:
        mesh.Mesh: The crate mesh
    """
    cx, cy, cz = center
    gen = BaseGenerator()

    if open_lid:
        for part in _open_box_shell(cx, cy, cz, width, depth, height):
            gen.add_mesh(part)
        top_cz = cz + height / 2 - _WALL_THICKNESS
        for part in _lid_rim(cx, cy, top_cz, width, depth,
                             rim_height=2.0, rim_thickness=1.5):
            gen.add_mesh(part)
    else:
        gen.add_mesh(_solid_box(cx, cy, cz, width, depth, height))

    # Raised border frame around each face (top, bottom, and one mid band)
    for part in _metal_band_detail(cx, cy, cz, width, depth, height,
                                   num_bands=1, band_height=2.0,
                                   band_protrude=0.5):
        gen.add_mesh(part)

    # Raised border rim at the very top and bottom
    hh = height / 2
    for z_pos in [cz - hh + 1.5, cz + hh - 1.5]:
        for part in _metal_band_detail(cx, cy, z_pos, width, depth, 0,
                                       num_bands=1, band_height=2.0,
                                       band_protrude=0.5):
            gen.add_mesh(part)

    if handle:
        hh = height / 2
        hd = depth / 2
        handle_cz = cz - hh + height * 0.6
        for part in _handle(cx, cy - hd, handle_cz, width):
            gen.add_mesh(part)
        for part in _handle(cx, cy + hd, handle_cz, width):
            part.vectors[:, :, 1] = 2 * (cy + hd) - part.vectors[:, :, 1]
            gen.add_mesh(part)

    return gen.combine()


def wooden_crate_with_bands(
    width: float = 20.0,
    depth: float = 18.0,
    height: float = 16.0,
    open_lid: bool = False,
    handle: bool = False,
    num_bands: int = 2,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> mesh.Mesh:
    """Create a wooden crate with decorative metal bands for 32mm miniatures.

    Combines wooden plank details with metal reinforcing bands wrapped
    around the body. No miniature base is attached.

    Args:
        width: Outer width in mm (X axis). Default 20 mm.
        depth: Outer depth in mm (Y axis). Default 18 mm.
        height: Outer height in mm (Z axis). Default 16 mm.
        open_lid: If True, the crate has an open top; if False, closed lid.
        handle: If True, add a D-ring handle on the front and back faces.
        num_bands: Number of metal bands. Default 2.
        center: (x, y, z) centre of the crate. Default (0, 0, 0).

    Returns:
        mesh.Mesh: The crate mesh
    """
    cx, cy, cz = center
    gen = BaseGenerator()

    if open_lid:
        for part in _open_box_shell(cx, cy, cz, width, depth, height):
            gen.add_mesh(part)
        top_cz = cz + height / 2 - _WALL_THICKNESS
        for part in _lid_rim(cx, cy, top_cz, width, depth,
                             rim_height=1.5, rim_thickness=1.5):
            gen.add_mesh(part)
    else:
        gen.add_mesh(_solid_box(cx, cy, cz, width, depth, height))

    # Plank line ridges
    for ridge in _plank_detail(cx, cy, cz, width, depth, height):
        gen.add_mesh(ridge)

    # Vertical corner strips
    for strip in _corner_strip_detail(cx, cy, cz, width, depth, height):
        gen.add_mesh(strip)

    # Metal bands over the wooden surface
    for band in _metal_band_detail(cx, cy, cz, width, depth, height,
                                   num_bands=num_bands):
        gen.add_mesh(band)

    if handle:
        hh = height / 2
        hd = depth / 2
        handle_cz = cz - hh + height * 0.6
        for part in _handle(cx, cy - hd, handle_cz, width):
            gen.add_mesh(part)
        for part in _handle(cx, cy + hd, handle_cz, width):
            part.vectors[:, :, 1] = 2 * (cy + hd) - part.vectors[:, :, 1]
            gen.add_mesh(part)

    return gen.combine()
