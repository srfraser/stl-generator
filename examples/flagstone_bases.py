"""Example: Creating miniature bases with flagstone patterns."""

from stl_generator.scenery import (
    flagstone_base_28mm,
    flagstone_base_32mm,
    add_flagstone_pattern,
)
from stl_generator.primitives import miniature_base_28mm
from stl_generator.generators import BaseGenerator

print("Creating flagstone pattern bases for tabletop gaming...\n")
print("=" * 70)

# Pattern 1: Irregular flagstones (default)
print("\n1. Creating 28mm base with IRREGULAR flagstone pattern...")
print("   - Random sized rectangular stones")
print("   - Natural, organic look")
base_irregular = flagstone_base_28mm(pattern="irregular", seed=42)
base_irregular.save("output_flagstone_irregular_28mm.stl")
print("   ✓ Created: output_flagstone_irregular_28mm.stl")

# Pattern 2: Rectangular flagstones
print("\n2. Creating 28mm base with RECTANGULAR flagstone pattern...")
print("   - Regular grid of stones")
print("   - Clean, orderly appearance")
base_rectangular = flagstone_base_28mm(pattern="rectangular", stone_size=4.0, gap=0.2)
base_rectangular.save("output_flagstone_rectangular_28mm.stl")
print("   ✓ Created: output_flagstone_rectangular_28mm.stl")

# Pattern 3: Hexagonal flagstones
print("\n3. Creating 28mm base with HEXAGONAL flagstone pattern...")
print("   - Honeycomb-like hexagonal tiles")
print("   - Geometric, stylized look")
base_hexagonal = flagstone_base_28mm(pattern="hexagonal", stone_size=4.5, gap=0.25)
base_hexagonal.save("output_flagstone_hexagonal_28mm.stl")
print("   ✓ Created: output_flagstone_hexagonal_28mm.stl")

# Pattern 4: Random Voronoi-like pattern
print("\n4. Creating 28mm base with RANDOM flagstone pattern...")
print("   - Organic, natural stone shapes")
print("   - Voronoi-like cells")
base_random = flagstone_base_28mm(pattern="random", num_stones=25, seed=123)
base_random.save("output_flagstone_random_28mm.stl")
print("   ✓ Created: output_flagstone_random_28mm.stl")

# Pattern 5: 32mm base with irregular pattern
print("\n5. Creating 32mm base with IRREGULAR flagstone pattern...")
print("   - Larger base for heroes/characters")
base_32_irregular = flagstone_base_32mm(pattern="irregular", seed=99)
base_32_irregular.save("output_flagstone_irregular_32mm.stl")
print("   ✓ Created: output_flagstone_irregular_32mm.stl")

# Pattern 6: Custom decorated base with specific parameters
print("\n6. Creating custom decorated base...")
print("   - Fine flagstones (smaller stones)")
print("   - Thin mortar gaps")
base_custom = flagstone_base_28mm(
    pattern="irregular",
    stone_height=0.2,  # Thinner stones
    gap=0.15,          # Narrow gaps
    seed=777
)
base_custom.save("output_flagstone_fine_28mm.stl")
print("   ✓ Created: output_flagstone_fine_28mm.stl")

# Create a warband set with different patterns
print("\n7. Creating a warband set (5 bases with different patterns)...")
warband = BaseGenerator()
patterns = ["irregular", "rectangular", "hexagonal", "random", "irregular"]
seeds = [1, 2, 3, 4, 5]

for i, (pattern, seed) in enumerate(zip(patterns, seeds)):
    base = miniature_base_28mm(center=(i * 35, 0, 0))
    decorated = add_flagstone_pattern(
        base,
        radius=14.0,
        base_height=3.5,
        pattern=pattern,
        stone_height=0.3,
        gap=0.3,
        seed=seed
    )
    warband.add_mesh(decorated)

warband.save("output_flagstone_warband.stl")
print("   ✓ Created: output_flagstone_warband.stl (5 varied bases)")

print("\n" + "=" * 70)
print("All flagstone bases created successfully!")
print("=" * 70)

print("\nPattern Summary:")
print("  • IRREGULAR   - Random sized rectangular stones (natural)")
print("  • RECTANGULAR - Regular grid pattern (orderly)")
print("  • HEXAGONAL   - Honeycomb hexagonal tiles (geometric)")
print("  • RANDOM      - Organic Voronoi-like shapes (natural)")

print("\nCustomization Tips:")
print("  • stone_height: Control how much stones protrude (0.2-0.5mm)")
print("  • gap: Width of mortar lines between stones (0.15-0.4mm)")
print("  • stone_size: Size of stones for rectangular/hexagonal patterns")
print("  • seed: Change random seed for pattern variation")

print("\nThese bases are ready for 3D printing and painting!")
