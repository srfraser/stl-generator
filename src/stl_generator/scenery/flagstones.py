"""Flagstone patterns and decorations for miniature bases."""

import numpy as np
from stl import mesh
from typing import Literal
from stl_generator.primitives import miniature_base_28mm, miniature_base_32mm
from stl_generator.generators import BaseGenerator

try:
    from scipy.spatial import Voronoi
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def _create_stone_mesh(vertices_2d: np.ndarray, z_base: float, height: float) -> mesh.Mesh:
    """
    Create a 3D mesh for a single flagstone from 2D vertices.

    Args:
        vertices_2d: 2D vertices of the stone polygon (N x 2)
        z_base: Z coordinate of the base
        height: Height of the stone

    Returns:
        mesh.Mesh: The stone mesh
    """
    n = len(vertices_2d)

    # Create 3D vertices (bottom and top)
    vertices_bottom = np.column_stack([vertices_2d, np.full(n, z_base)])
    vertices_top = np.column_stack([vertices_2d, np.full(n, z_base + height)])

    faces = []

    # Top face (fan triangulation from first vertex)
    for i in range(1, n - 1):
        faces.append([n + 0, n + i, n + i + 1])

    # Bottom face (fan triangulation from first vertex, reversed winding)
    for i in range(1, n - 1):
        faces.append([0, i + 1, i])

    # Side faces
    for i in range(n):
        next_i = (i + 1) % n
        # Two triangles per side
        faces.append([i, next_i, n + i])
        faces.append([next_i, n + next_i, n + i])

    faces = np.array(faces)

    # Create the mesh
    all_vertices = np.vstack([vertices_bottom, vertices_top])
    stone_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))

    for i, face in enumerate(faces):
        for j in range(3):
            stone_mesh.vectors[i][j] = all_vertices[face[j]]

    return stone_mesh


def _generate_rectangular_pattern(radius: float, gap: float, stone_size: float) -> list:
    """
    Generate rectangular flagstone pattern extending beyond the rim.

    Stones are generated across the full grid and will be clipped to the
    circular boundary later for full coverage.
    """
    stones = []

    # Create a grid of rectangular stones extending beyond the circle
    num_stones = int(radius * 2 / stone_size) + 2
    start = -radius - stone_size / 2

    for i in range(num_stones):
        for j in range(num_stones):
            x = start + i * stone_size
            y = start + j * stone_size

            # Create rectangle vertices (without gap - gap applied after clipping)
            rect = np.array([
                [x, y],
                [x + stone_size, y],
                [x + stone_size, y + stone_size],
                [x, y + stone_size],
            ])

            # Include stone if any part might be within the circle
            center = rect.mean(axis=0)
            if np.sqrt(center[0]**2 + center[1]**2) < radius + stone_size:
                stones.append(rect)

    return stones


def _generate_irregular_pattern(radius: float, gap: float, seed: int = 42) -> list:
    """
    Generate irregular flagstone pattern with varied sizes using grid-based placement.

    Uses a jittered grid approach to ensure good coverage while maintaining
    an irregular, natural appearance.
    """
    np.random.seed(seed)
    stones = []

    # Base grid cell size - use larger cells for better coverage
    base_size = radius / 3.5

    # Grid parameters - extend beyond rim for edge clipping
    grid_range = int(radius / base_size) + 2

    for i in range(-grid_range, grid_range + 1):
        for j in range(-grid_range, grid_range + 1):
            # Base position at cell center
            base_x = (i + 0.5) * base_size
            base_y = (j + 0.5) * base_size

            # Small random offset for organic look
            jitter = base_size * 0.08
            x = base_x + np.random.uniform(-jitter, jitter)
            y = base_y + np.random.uniform(-jitter, jitter)

            # Skip if too far from circle
            if np.sqrt(x**2 + y**2) >= radius + base_size:
                continue

            # Size fills the cell fully (slight overlap allowed since we shrink later)
            size_x = base_size * np.random.uniform(0.98, 1.02)
            size_y = base_size * np.random.uniform(0.98, 1.02)

            # Create irregular quadrilateral by perturbing corners
            corner_jitter = base_size * 0.06
            corners = [
                [x - size_x/2, y - size_y/2],
                [x + size_x/2, y - size_y/2],
                [x + size_x/2, y + size_y/2],
                [x - size_x/2, y + size_y/2],
            ]

            # Add small random perturbation to each corner for irregular look
            for corner in corners:
                corner[0] += np.random.uniform(-corner_jitter, corner_jitter)
                corner[1] += np.random.uniform(-corner_jitter, corner_jitter)

            stones.append(np.array(corners))

    return stones


def _generate_hexagonal_pattern(radius: float, gap: float, stone_size: float) -> list:
    """
    Generate hexagonal flagstone pattern with proper tessellation.

    Hexagons are generated extending beyond the rim and will be clipped
    to the circular boundary for full coverage.
    """
    stones = []

    # For flat-top hexagons (vertices pointing left/right):
    # - Outer radius R = stone_size / 2 (center to vertex)
    # - Width = 2R, Height = sqrt(3) * R
    # Grid spacing for tessellation:
    # - Horizontal: 1.5 * R (centers overlap horizontally)
    # - Vertical: sqrt(3) * R (full height)
    # - Offset every other column by half the height

    hex_radius = stone_size / 2  # Virtual radius for grid spacing
    horiz_spacing = 1.5 * hex_radius
    vert_spacing = np.sqrt(3) * hex_radius

    # Full hexagon radius (gap applied after clipping)
    draw_radius = hex_radius

    # Grid parameters - extend beyond the rim
    cols = int(radius * 2 / horiz_spacing) + 3
    rows = int(radius * 2 / vert_spacing) + 3

    for row in range(-rows, rows):
        for col in range(-cols, cols):
            # Offset every other column vertically
            x = col * horiz_spacing
            y = row * vert_spacing + (vert_spacing / 2 if col % 2 else 0)

            # Create hexagon vertices (flat-top orientation)
            hex_verts = []
            for i in range(6):
                angle = np.pi / 3 * i
                vx = x + draw_radius * np.cos(angle)
                vy = y + draw_radius * np.sin(angle)
                hex_verts.append([vx, vy])

            hex_verts = np.array(hex_verts)

            # Include hexagon if any part might be within the circle
            if np.sqrt(x**2 + y**2) < radius + stone_size:
                stones.append(hex_verts)

    return stones


def _clip_polygon_to_circle(polygon: np.ndarray, radius: float) -> np.ndarray:
    """
    Clip a polygon to a circle using Sutherland-Hodgman-like approach.

    Args:
        polygon: 2D polygon vertices (N x 2)
        radius: Clipping circle radius

    Returns:
        Clipped polygon vertices, or empty array if polygon is entirely outside
    """
    if len(polygon) < 3:
        return np.array([])

    clipped = []
    n = len(polygon)

    for i in range(n):
        curr = polygon[i]
        next_pt = polygon[(i + 1) % n]

        curr_dist = np.sqrt(curr[0]**2 + curr[1]**2)
        next_dist = np.sqrt(next_pt[0]**2 + next_pt[1]**2)

        curr_inside = curr_dist <= radius
        next_inside = next_dist <= radius

        if curr_inside:
            clipped.append(list(curr))

        # If edge crosses the circle boundary, find intersection
        if curr_inside != next_inside:
            dx = next_pt[0] - curr[0]
            dy = next_pt[1] - curr[1]
            # Solve: |curr + t*d|^2 = radius^2
            a = dx*dx + dy*dy
            if a > 1e-10:  # Avoid division by zero
                b = 2 * (curr[0]*dx + curr[1]*dy)
                c = curr[0]**2 + curr[1]**2 - radius**2
                discriminant = b*b - 4*a*c
                if discriminant >= 0:
                    sqrt_disc = np.sqrt(discriminant)
                    t1 = (-b - sqrt_disc) / (2*a)
                    t2 = (-b + sqrt_disc) / (2*a)
                    # Choose the t in (0, 1) - the intersection point along the edge
                    for t in sorted([t1, t2]):
                        if 0 < t < 1:
                            intersection = [curr[0] + t*dx, curr[1] + t*dy]
                            clipped.append(intersection)
                            break

    if len(clipped) < 3:
        return np.array([])

    return np.array(clipped)


def _generate_random_voronoi_pattern_scipy(radius: float, gap: float, num_stones: int, seed: int) -> list:
    """
    Generate random Voronoi flagstone pattern using scipy (proper tessellation).

    Seeds are distributed across the full circle and Voronoi cells are
    clipped to the boundary for full coverage.
    """
    np.random.seed(seed)
    stones = []

    # Generate random points as Voronoi seeds within and slightly beyond the circle
    # Use rejection sampling to get uniform distribution
    points = []
    target_points = int(num_stones * 1.2)  # Generate extra for edge coverage
    while len(points) < target_points:
        x = np.random.uniform(-radius * 1.1, radius * 1.1)
        y = np.random.uniform(-radius * 1.1, radius * 1.1)
        if x*x + y*y < (radius * 1.1)**2:
            points.append([x, y])

    points = np.array(points)

    # Add boundary points to bound the Voronoi diagram
    boundary_dist = radius * 3
    boundary_points = [
        [-boundary_dist, -boundary_dist],
        [-boundary_dist, 0],
        [-boundary_dist, boundary_dist],
        [0, -boundary_dist],
        [0, boundary_dist],
        [boundary_dist, -boundary_dist],
        [boundary_dist, 0],
        [boundary_dist, boundary_dist],
    ]

    all_points = np.vstack([points, boundary_points])

    # Compute Voronoi diagram
    vor = Voronoi(all_points)

    # Extract finite Voronoi regions for our seed points (not boundary points)
    for point_idx in range(len(points)):
        region_idx = vor.point_region[point_idx]
        region = vor.regions[region_idx]

        # Skip infinite regions (shouldn't happen with boundary points)
        if -1 in region or len(region) < 3:
            continue

        # Get the polygon vertices
        polygon = np.array([vor.vertices[i] for i in region])

        # Only include if the seed point is within the circle
        seed_point = points[point_idx]
        if np.sqrt(seed_point[0]**2 + seed_point[1]**2) > radius:
            continue

        # Return raw polygon - clipping and gap applied later
        stones.append(polygon)

    return stones


def _generate_random_voronoi_pattern_fallback(radius: float, gap: float, num_stones: int, seed: int) -> list:
    """
    Generate random-looking flagstone pattern without scipy.

    Uses irregular quadrilaterals on a hexagonal grid for an organic,
    cobblestone-like appearance with high coverage.
    """
    np.random.seed(seed)
    stones = []

    # Calculate cell size based on desired density
    stone_area = np.pi * radius**2 / num_stones
    cell_size = np.sqrt(stone_area * 1.2)

    # Use staggered rows (like brick pattern) for good coverage
    horiz_spacing = cell_size
    vert_spacing = cell_size * 0.9

    grid_cols = int(radius * 2 / horiz_spacing) + 3
    grid_rows = int(radius * 2 / vert_spacing) + 3

    for row in range(-grid_rows, grid_rows + 1):
        for col in range(-grid_cols, grid_cols + 1):
            # Staggered row offset
            cx = col * horiz_spacing
            if row % 2:
                cx += horiz_spacing / 2
            cy = row * vert_spacing

            # Small jitter for organic look
            jitter = cell_size * 0.1
            cx += np.random.uniform(-jitter, jitter)
            cy += np.random.uniform(-jitter, jitter)

            # Include if might intersect the circle
            if np.sqrt(cx**2 + cy**2) >= radius + cell_size:
                continue

            # Create irregular quadrilateral that fills most of the cell
            half_size = cell_size * 0.48

            # Base corners with random variation
            corner_var = cell_size * 0.08
            corners = [
                [cx - half_size + np.random.uniform(-corner_var, corner_var),
                 cy - half_size + np.random.uniform(-corner_var, corner_var)],
                [cx + half_size + np.random.uniform(-corner_var, corner_var),
                 cy - half_size + np.random.uniform(-corner_var, corner_var)],
                [cx + half_size + np.random.uniform(-corner_var, corner_var),
                 cy + half_size + np.random.uniform(-corner_var, corner_var)],
                [cx - half_size + np.random.uniform(-corner_var, corner_var),
                 cy + half_size + np.random.uniform(-corner_var, corner_var)],
            ]

            stones.append(np.array(corners))

    return stones


def _generate_random_voronoi_pattern(radius: float, gap: float, num_stones: int = 30, seed: int = 42) -> list:
    """Generate random Voronoi-like flagstone pattern with proper tessellation."""
    if HAS_SCIPY:
        return _generate_random_voronoi_pattern_scipy(radius, gap, num_stones, seed)
    else:
        return _generate_random_voronoi_pattern_fallback(radius, gap, num_stones, seed)


def _shrink_polygon(polygon: np.ndarray, gap: float) -> np.ndarray:
    """
    Shrink a polygon towards its centroid to create gaps between stones.

    Each edge moves inward by approximately 'gap' distance from its original
    position, creating mortar lines of width 'gap' between adjacent stones.

    Args:
        polygon: 2D polygon vertices (N x 2)
        gap: Distance to move each edge inward

    Returns:
        Shrunk polygon vertices
    """
    if len(polygon) < 3:
        return polygon

    centroid = polygon.mean(axis=0)

    # Calculate the minimum distance from centroid to any edge
    # This gives a better estimate of polygon "radius" than average vertex distance
    n = len(polygon)
    min_edge_dist = float('inf')

    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]

        # Vector from p1 to p2
        edge = p2 - p1
        edge_len = np.sqrt(edge[0]**2 + edge[1]**2)

        if edge_len < 1e-10:
            continue

        # Project centroid onto the edge line
        t = np.dot(centroid - p1, edge) / (edge_len * edge_len)
        t = np.clip(t, 0, 1)

        # Closest point on edge to centroid
        closest = p1 + t * edge
        dist = np.sqrt(np.sum((centroid - closest)**2))
        min_edge_dist = min(min_edge_dist, dist)

    # Shrink factor: move each vertex toward centroid so edges move inward by gap
    if min_edge_dist > gap * 1.5:
        shrink_factor = 1 - gap / min_edge_dist
        shrink_factor = max(0.7, shrink_factor)  # Don't shrink too much
    else:
        shrink_factor = 0.85

    return centroid + (polygon - centroid) * shrink_factor


def add_flagstone_pattern(
    base_mesh: mesh.Mesh,
    radius: float,
    base_height: float,
    pattern: Literal["rectangular", "irregular", "hexagonal", "random"] = "irregular",
    stone_height: float = 0.3,
    gap: float = 0.2,
    stone_size: float = None,
    num_stones: int = 30,
    seed: int = 42
) -> mesh.Mesh:
    """
    Add a flagstone pattern to the top of a base mesh.

    Patterns are generated extending beyond the rim and then clipped to the
    circular boundary, ensuring high coverage (90%+) of the top surface.

    Args:
        base_mesh: The base mesh to decorate
        radius: Radius of the base
        base_height: Height of the base
        pattern: Pattern type ("rectangular", "irregular", "hexagonal", "random")
        stone_height: Height of the flagstones above the base surface (mm)
        gap: Gap between stones for mortar (mm). Default 0.2 for 90%+ coverage.
        stone_size: Size of stones (used for rectangular/hexagonal patterns)
        num_stones: Number of stones (used for random pattern)
        seed: Random seed for reproducibility

    Returns:
        mesh.Mesh: Combined mesh with base and flagstones
    """
    generator = BaseGenerator()
    generator.add_mesh(base_mesh)

    # Default stone size based on radius - sized for 90%+ coverage with default gap
    if stone_size is None:
        stone_size = radius / 2.5

    # Generate stone pattern (raw polygons extending beyond rim)
    if pattern == "rectangular":
        raw_stones = _generate_rectangular_pattern(radius, gap, stone_size)
    elif pattern == "irregular":
        raw_stones = _generate_irregular_pattern(radius, gap, seed)
    elif pattern == "hexagonal":
        raw_stones = _generate_hexagonal_pattern(radius, gap, stone_size)
    elif pattern == "random":
        raw_stones = _generate_random_voronoi_pattern(radius, gap, num_stones, seed)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")

    # Clip radius - the visible edge of the base
    clip_radius = radius - gap / 2

    # Process each stone: shrink for gap first, then clip to circle
    # This ensures edge stones maintain proper proportions after clipping
    z_base = base_height / 2  # Top of the base

    for stone_verts in raw_stones:
        # First shrink for mortar gaps (creates the gap between adjacent stones)
        shrunk = _shrink_polygon(np.array(stone_verts), gap / 2)

        if len(shrunk) < 3:
            continue

        # Then clip to circular boundary
        final_stone = _clip_polygon_to_circle(shrunk, clip_radius)

        if len(final_stone) < 3:
            continue

        # Check that stone has meaningful area (not degenerate)
        x_span = final_stone[:, 0].max() - final_stone[:, 0].min()
        y_span = final_stone[:, 1].max() - final_stone[:, 1].min()
        if x_span < gap or y_span < gap:
            continue

        stone_mesh = _create_stone_mesh(final_stone, z_base, stone_height)
        generator.add_mesh(stone_mesh)

    return generator.combine()


def flagstone_base_28mm(
    pattern: Literal["rectangular", "irregular", "hexagonal", "random"] = "irregular",
    stone_height: float = 0.3,
    gap: float = 0.2,
    stone_size: float = None,
    num_stones: int = 30,
    seed: int = 42
) -> mesh.Mesh:
    """
    Create a 28mm base with flagstone pattern.

    Args:
        pattern: Pattern type ("rectangular", "irregular", "hexagonal", "random")
        stone_height: Height of the flagstones above the base surface (mm)
        gap: Gap between stones for mortar (mm)
        stone_size: Size of stones (used for rectangular/hexagonal patterns)
        num_stones: Number of stones (used for random pattern)
        seed: Random seed for reproducibility

    Returns:
        mesh.Mesh: The decorated base mesh
    """
    base = miniature_base_28mm()
    return add_flagstone_pattern(
        base,
        radius=14.0,
        base_height=3.5,
        pattern=pattern,
        stone_height=stone_height,
        gap=gap,
        stone_size=stone_size,
        num_stones=num_stones,
        seed=seed
    )


def flagstone_base_32mm(
    pattern: Literal["rectangular", "irregular", "hexagonal", "random"] = "irregular",
    stone_height: float = 0.3,
    gap: float = 0.2,
    stone_size: float = None,
    num_stones: int = 35,
    seed: int = 42
) -> mesh.Mesh:
    """
    Create a 32mm base with flagstone pattern.

    Args:
        pattern: Pattern type ("rectangular", "irregular", "hexagonal", "random")
        stone_height: Height of the flagstones above the base surface (mm)
        gap: Gap between stones for mortar (mm)
        stone_size: Size of stones (used for rectangular/hexagonal patterns)
        num_stones: Number of stones (used for random pattern)
        seed: Random seed for reproducibility

    Returns:
        mesh.Mesh: The decorated base mesh
    """
    base = miniature_base_32mm()
    return add_flagstone_pattern(
        base,
        radius=16.0,
        base_height=4.0,
        pattern=pattern,
        stone_height=stone_height,
        gap=gap,
        stone_size=stone_size,
        num_stones=num_stones,
        seed=seed
    )
