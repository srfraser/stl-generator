"""Example: Creating basic shapes and saving them as STL files."""

from stl_generator.primitives import cube, sphere, cylinder, cone

# Create and save basic shapes
print("Creating basic shapes...")

# Cube
cube_mesh = cube(size=20, center=(0, 0, 0))
cube_mesh.save("output_cube.stl")
print("Created: output_cube.stl")

# Sphere
sphere_mesh = sphere(radius=15, center=(0, 0, 0), resolution=30)
sphere_mesh.save("output_sphere.stl")
print("Created: output_sphere.stl")

# Cylinder
cylinder_mesh = cylinder(radius=10, height=30, center=(0, 0, 0), resolution=32)
cylinder_mesh.save("output_cylinder.stl")
print("Created: output_cylinder.stl")

# Cone
cone_mesh = cone(radius=15, height=25, center=(0, 0, 0), resolution=32)
cone_mesh.save("output_cone.stl")
print("Created: output_cone.stl")

print("\nAll shapes created successfully!")
