"""Example: Combining multiple shapes to create complex objects."""

from stl_generator.primitives import cube, sphere, cylinder
from stl_generator.generators import BaseGenerator

print("Creating a snowman from combined shapes...")

# Create a snowman using three spheres
generator = BaseGenerator()

# Bottom sphere (largest)
bottom = sphere(radius=20, center=(0, 0, 0), resolution=30)
generator.add_mesh(bottom)

# Middle sphere
middle = sphere(radius=15, center=(0, 0, 30), resolution=30)
generator.add_mesh(middle)

# Top sphere (head)
head = sphere(radius=10, center=(0, 0, 50), resolution=30)
generator.add_mesh(head)

# Save the snowman
generator.save("output_snowman.stl")
print("Created: output_snowman.stl")


print("\nCreating a table...")

# Create a simple table
table = BaseGenerator()

# Table top
top = cube(size=50, center=(0, 0, 30))
top.vectors[:, :, 2] *= 0.1  # Make it thin
table.add_mesh(top)

# Table legs (4 cylinders)
leg_positions = [(-20, -20, 0), (20, -20, 0), (-20, 20, 0), (20, 20, 0)]
for pos in leg_positions:
    leg = cylinder(radius=2, height=30, center=pos, resolution=16)
    table.add_mesh(leg)

table.save("output_table.stl")
print("Created: output_table.stl")

print("\nAll complex shapes created successfully!")
