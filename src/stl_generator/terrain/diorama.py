"""Terrain pieces for 32mm fantasy miniature dioramas.

Includes dungeon floors, stone walls, and cobblestone streets sized for
dungeons, fantasy towns, gaols, and necromancer lairs at 32mm scale.
"""

import numpy as np
from stl import mesh
from stl_generator.primitives import box
from stl_generator.generators import BaseGenerator

# 32mm scale constant: 1mm in real life ≈ 1.8mm at 32mm heroic scale
# All default dimensions are in mm and tuned for 32mm miniatures.


def dungeon_floor_tile(
    width: float = 50.0,
    depth: float = 50.0,
    thickness: float = 5.0,
    stone_size: float = 10.0,
    gap: float = 0.8,
    stone_height: float = 0.5,
) -> mesh.Mesh:
    """
    Create a rectangular dungeon floor tile with raised flagstone pattern.

    Scaled for 32mm miniatures.  Default size is 50×50mm, which fits a
    two-by-two grid under a standard 32mm base.  Stones are laid in a
    regular grid and protrude slightly above the base surface to give a
    flagstone appearance.

    Args:
        width: Tile width along X axis in mm (default 50)
        depth: Tile depth along Y axis in mm (default 50)
        thickness: Tile thickness in mm (default 5)
        stone_size: Approximate size of each flagstone in mm (default 10)
        gap: Gap (mortar line) between stones in mm (default 0.8)
        stone_height: How far stones protrude above the tile surface (default 0.5)

    Returns:
        mesh.Mesh: The floor tile mesh
    """
    generator = BaseGenerator()

    # Base tile, centred at origin
    base = box(width=width, depth=depth, height=thickness)
    generator.add_mesh(base)

    z_surface = thickness / 2  # Top surface of the base tile

    # Number of stones that fit across each axis
    num_x = max(1, int(width / stone_size))
    num_y = max(1, int(depth / stone_size))

    # Actual stone dimensions (equal subdivision minus gap on each side)
    cell_w = width / num_x
    cell_d = depth / num_y
    stone_w = cell_w - gap
    stone_d = cell_d - gap

    # Origin corner of the tile in XY
    origin_x = -width / 2
    origin_y = -depth / 2

    for ix in range(num_x):
        for iy in range(num_y):
            # Stone lower-left corner
            sx = origin_x + ix * cell_w + gap / 2
            sy = origin_y + iy * cell_d + gap / 2

            stone = box(
                width=stone_w,
                depth=stone_d,
                height=stone_height,
                center=(sx + stone_w / 2, sy + stone_d / 2,
                        z_surface + stone_height / 2),
            )
            generator.add_mesh(stone)

    return generator.combine()


def dungeon_wall_section(
    width: float = 50.0,
    height: float = 40.0,
    thickness: float = 8.0,
    course_height: float = 8.0,
    stone_length: float = 14.0,
    gap: float = 0.8,
    relief: float = 0.5,
) -> mesh.Mesh:
    """
    Create a dungeon wall section with embossed stone courses.

    The wall is a solid rectangular block with raised stone blocks on its
    front face arranged in staggered courses (like real masonry), giving a
    classic dungeon-stone appearance.  Scaled for 32mm miniatures.

    Args:
        width: Wall width along X axis in mm (default 50)
        height: Wall height along Z axis in mm (default 40)
        thickness: Wall thickness along Y axis in mm (default 8)
        course_height: Height of each stone course in mm (default 8)
        stone_length: Length of each stone block in mm (default 14)
        gap: Mortar gap between stones in mm (default 0.8)
        relief: How far stones protrude from the wall face in mm (default 0.5)

    Returns:
        mesh.Mesh: The wall section mesh
    """
    generator = BaseGenerator()

    # Main wall body, centred at origin
    base = box(width=width, depth=thickness, height=height)
    generator.add_mesh(base)

    # Front face of the wall is at y = -thickness/2;
    # stone centres are at y = -(thickness/2 + relief/2)
    y_face = -thickness / 2
    stone_w = stone_length - gap
    stone_h = course_height - gap

    num_courses = max(1, int(height / course_height))
    num_stones = max(1, int(width / stone_length))

    origin_z = -height / 2
    origin_x = -width / 2

    for ic in range(num_courses):
        # Stagger alternate courses by half a stone length (classic ashlar bond)
        offset_x = (stone_length / 2) if ic % 2 else 0.0
        sz = origin_z + ic * course_height + gap / 2

        for is_ in range(-1, num_stones + 1):
            sx = origin_x + is_ * stone_length + offset_x + gap / 2

            # Only include stones that overlap the wall width
            stone_left = sx
            stone_right = sx + stone_w
            if stone_right <= origin_x or stone_left >= origin_x + width:
                continue

            # Clip stone to wall width
            clipped_left = max(stone_left, origin_x)
            clipped_right = min(stone_right, origin_x + width)
            clipped_w = clipped_right - clipped_left
            if clipped_w <= gap:
                continue

            stone_cx = (clipped_left + clipped_right) / 2
            stone_cz = sz + stone_h / 2
            stone_cy = y_face - relief / 2

            stone = box(
                width=clipped_w,
                depth=relief,
                height=stone_h,
                center=(stone_cx, stone_cy, stone_cz),
            )
            generator.add_mesh(stone)

    return generator.combine()


def cobblestone_street_tile(
    width: float = 50.0,
    depth: float = 50.0,
    thickness: float = 5.0,
    stone_size: float = 7.0,
    gap: float = 0.6,
    stone_height: float = 0.5,
) -> mesh.Mesh:
    """
    Create a cobblestone street tile for fantasy towns.

    Cobblestones are arranged in a staggered-row pattern (offset every other
    row) to give an organic, hand-laid appearance typical of medieval streets.
    Scaled for 32mm miniatures.

    Args:
        width: Tile width along X axis in mm (default 50)
        depth: Tile depth along Y axis in mm (default 50)
        thickness: Tile thickness in mm (default 5)
        stone_size: Approximate cobblestone diameter in mm (default 7)
        gap: Gap between cobblestones in mm (default 0.6)
        stone_height: How far cobblestones protrude above the tile surface (default 0.5)

    Returns:
        mesh.Mesh: The cobblestone street tile mesh
    """
    generator = BaseGenerator()

    base = box(width=width, depth=depth, height=thickness)
    generator.add_mesh(base)

    z_surface = thickness / 2

    cell_size = stone_size + gap
    stone_w = stone_size - gap / 2
    stone_d = stone_size - gap / 2

    # Use a hexagonal-row stagger for cobblestone feel
    num_rows = max(1, int(depth / cell_size)) + 1
    num_cols = max(1, int(width / cell_size)) + 1

    origin_x = -width / 2
    origin_y = -depth / 2

    for row in range(num_rows):
        # Offset every other row by half a stone cell
        x_offset = (cell_size / 2) if row % 2 else 0.0
        cy = origin_y + row * cell_size + gap / 2

        for col in range(-1, num_cols + 1):
            cx = origin_x + col * cell_size + x_offset + gap / 2

            stone_right = cx + stone_w
            stone_top = cy + stone_d

            # Skip stones fully outside the tile
            if stone_right <= origin_x or cx >= origin_x + width:
                continue
            if stone_top <= origin_y or cy >= origin_y + depth:
                continue

            # Clip to tile boundary
            clipped_left = max(cx, origin_x)
            clipped_right = min(stone_right, origin_x + width)
            clipped_bottom = max(cy, origin_y)
            clipped_top = min(stone_top, origin_y + depth)
            clipped_w = clipped_right - clipped_left
            clipped_d = clipped_top - clipped_bottom

            if clipped_w <= gap or clipped_d <= gap:
                continue

            stone_cx = (clipped_left + clipped_right) / 2
            stone_cy_center = (clipped_bottom + clipped_top) / 2

            stone = box(
                width=clipped_w,
                depth=clipped_d,
                height=stone_height,
                center=(stone_cx, stone_cy_center,
                        z_surface + stone_height / 2),
            )
            generator.add_mesh(stone)

    return generator.combine()
