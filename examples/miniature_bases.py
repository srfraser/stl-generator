"""Example: Creating standard miniature bases for tabletop gaming."""

from stl_generator.primitives import miniature_base_28mm, miniature_base_32mm
from stl_generator.generators import BaseGenerator

print("Creating miniature bases for tabletop gaming...\n")

# Create a single 28mm base
print("Creating 28mm base (28mm diameter, 3.5mm height)")
base_28 = miniature_base_28mm(center=(0, 0, 0))
base_28.save("output_base_28mm.stl")
print("Created: output_base_28mm.stl")

# Create a single 32mm base
print("\nCreating 32mm base (32mm diameter, 4mm height)")
base_32 = miniature_base_32mm(center=(0, 0, 0))
base_32.save("output_base_32mm.stl")
print("Created: output_base_32mm.stl")

# Create a squad of bases (5x 28mm bases in a line)
print("\nCreating a squad of 5x 28mm bases...")
squad = BaseGenerator()
spacing = 35  # 35mm spacing between base centers

for i in range(5):
    x_pos = i * spacing
    base = miniature_base_28mm(center=(x_pos, 0, 0))
    squad.add_mesh(base)

squad.save("output_squad_bases_28mm.stl")
print("Created: output_squad_bases_28mm.stl")

# Create a mixed unit (3x 32mm bases for heroes)
print("\nCreating a hero unit of 3x 32mm bases...")
heroes = BaseGenerator()

for i in range(3):
    x_pos = i * 40  # 40mm spacing for larger bases
    base = miniature_base_32mm(center=(x_pos, 0, 0))
    heroes.add_mesh(base)

heroes.save("output_hero_bases_32mm.stl")
print("Created: output_hero_bases_32mm.stl")

# Create a grid of bases for batch printing
print("\nCreating a 3x3 grid of 28mm bases for batch printing...")
grid = BaseGenerator()
spacing = 32  # Tight spacing for efficient printing

for row in range(3):
    for col in range(3):
        x_pos = col * spacing
        y_pos = row * spacing
        base = miniature_base_28mm(center=(x_pos, y_pos, 0))
        grid.add_mesh(base)

grid.save("output_base_grid_28mm.stl")
print("Created: output_base_grid_28mm.stl (9 bases)")

print("\n" + "="*60)
print("All miniature bases created successfully!")
print("="*60)
print("\nBase specifications:")
print("  28mm base: 28mm diameter × 3.5mm height")
print("  32mm base: 32mm diameter × 4mm height")
print("\nThese are standard sizes for tabletop wargaming miniatures.")
