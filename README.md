# STL Generator

Generate STL files programmatically or from LLM prompts using Python.

## Features

- **Primitive Shapes**: Create basic 3D shapes (cube, sphere, cylinder, cone)
- **Miniature Bases**: Standard 28mm and 32mm bases for tabletop gaming
- **Scenic Bases**: Flagstone patterns (rectangular, irregular, hexagonal, random) for detailed terrain
- **Shape Composition**: Combine multiple shapes to create complex objects
- **Transformations**: Translate, rotate, and scale meshes
- **LLM Integration**: Generate STL files from natural language descriptions using Claude
- **Easy to Use**: Simple, intuitive API

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

## Quick Start

### Basic Shapes

```python
from stl_generator.primitives import cube, sphere, cylinder, cone

# Create a cube
cube_mesh = cube(size=20, center=(0, 0, 0))
cube_mesh.save("my_cube.stl")

# Create a sphere
sphere_mesh = sphere(radius=15, resolution=30)
sphere_mesh.save("my_sphere.stl")

# Create a cylinder
cylinder_mesh = cylinder(radius=10, height=30)
cylinder_mesh.save("my_cylinder.stl")

# Create a cone
cone_mesh = cone(radius=15, height=25)
cone_mesh.save("my_cone.stl")
```

### Miniature Bases

Create standard tabletop gaming miniature bases:

```python
from stl_generator.primitives import miniature_base_28mm, miniature_base_32mm
from stl_generator.generators import BaseGenerator

# Single 28mm base (28mm diameter, 3.5mm height)
base_28 = miniature_base_28mm()
base_28.save("base_28mm.stl")

# Single 32mm base (32mm diameter, 4mm height)
base_32 = miniature_base_32mm()
base_32.save("base_32mm.stl")

# Create a squad of bases
squad = BaseGenerator()
for i in range(5):
    base = miniature_base_28mm(center=(i * 35, 0, 0))
    squad.add_mesh(base)
squad.save("squad_bases.stl")
```

### Flagstone Scenic Bases

Add detailed flagstone patterns to your bases:

```python
from stl_generator.scenery import flagstone_base_28mm, flagstone_base_32mm

# Irregular flagstone pattern (natural look)
base_irregular = flagstone_base_28mm(pattern="irregular", seed=42)
base_irregular.save("flagstone_irregular.stl")

# Rectangular pattern (orderly grid)
base_rect = flagstone_base_28mm(pattern="rectangular", stone_size=4.0)
base_rect.save("flagstone_rectangular.stl")

# Hexagonal pattern (honeycomb)
base_hex = flagstone_base_28mm(pattern="hexagonal", stone_size=4.5)
base_hex.save("flagstone_hexagonal.stl")

# Random organic pattern (Voronoi-like)
base_random = flagstone_base_28mm(pattern="random", num_stones=25)
base_random.save("flagstone_random.stl")

# Customize stone height and mortar gap
base_custom = flagstone_base_28mm(
    pattern="irregular",
    stone_height=0.5,  # Taller stones (mm)
    gap=0.2,           # Narrow mortar gaps (mm)
    seed=123
)
base_custom.save("flagstone_custom.stl")
```

### Combining Shapes

```python
from stl_generator.primitives import sphere, cylinder
from stl_generator.generators import BaseGenerator

# Create a dumbbell
dumbbell = BaseGenerator()

# Left weight
left_weight = sphere(radius=10, center=(-25, 0, 0))
dumbbell.add_mesh(left_weight)

# Bar
bar = cylinder(radius=2, height=50, center=(0, 0, 0))
bar.vectors[:, :, 2] = bar.vectors[:, :, 1]  # Rotate to horizontal
bar.vectors[:, :, 1] = 0
dumbbell.add_mesh(bar)

# Right weight
right_weight = sphere(radius=10, center=(25, 0, 0))
dumbbell.add_mesh(right_weight)

# Save
dumbbell.save("dumbbell.stl")
```

### Transformations

```python
from stl_generator.primitives import cube
from stl_generator.generators import BaseGenerator

gen = BaseGenerator()
gen.add_mesh(cube(size=10))

# Transform the mesh
gen.translate(dx=5, dy=10, dz=0)  # Move
gen.rotate_z(45)                   # Rotate 45 degrees around Z axis
gen.scale(sx=2, sy=1, sz=1)        # Scale (stretch along X)

gen.save("transformed_cube.stl")
```

### LLM-Based Generation

Generate STL files from natural language descriptions using Claude:

```python
from stl_generator.llm import LLMGenerator

# Set your API key
# export ANTHROPIC_API_KEY='your-key-here'

generator = LLMGenerator()

# Generate from a prompt
code = generator.generate_from_prompt(
    prompt="Create a simple house with a cube base and a cone roof",
    filename="house.stl",
    execute=True  # Automatically execute and save
)

print(f"Generated code:\n{code}")
```

## API Reference

### Primitives

#### `cube(size, center=(0,0,0))`
Create a cube mesh.

- `size`: Length of each side
- `center`: Center point (x, y, z)

#### `sphere(radius, center=(0,0,0), resolution=20)`
Create a sphere mesh.

- `radius`: Radius of the sphere
- `center`: Center point (x, y, z)
- `resolution`: Number of segments (higher = smoother)

#### `cylinder(radius, height, center=(0,0,0), resolution=32)`
Create a cylinder mesh.

- `radius`: Radius of the cylinder
- `height`: Height of the cylinder
- `center`: Center point (x, y, z)
- `resolution`: Number of segments around circumference

#### `cone(radius, height, center=(0,0,0), resolution=32)`
Create a cone mesh.

- `radius`: Radius of the base
- `height`: Height of the cone
- `center`: Center point of the base (x, y, z)
- `resolution`: Number of segments around circumference

#### `miniature_base_28mm(center=(0,0,0), resolution=32)`
Create a standard 28mm miniature base for tabletop gaming.

- Dimensions: 28mm diameter × 3.5mm height
- Common for standard troops in games like Warhammer 40k
- `center`: Center point of the base (x, y, z)
- `resolution`: Number of segments around circumference

#### `miniature_base_32mm(center=(0,0,0), resolution=32)`
Create a standard 32mm miniature base for tabletop gaming.

- Dimensions: 32mm diameter × 4mm height
- Common for heroes and larger models in games like Warhammer 40k
- `center`: Center point of the base (x, y, z)
- `resolution`: Number of segments around circumference

### Scenic Bases

#### `flagstone_base_28mm(pattern="irregular", stone_height=0.3, gap=0.3, stone_size=None, num_stones=30, seed=42)`
Create a 28mm base with flagstone pattern.

- `pattern`: Pattern type - "irregular", "rectangular", "hexagonal", or "random"
  - **irregular**: Random sized rectangular stones (natural look)
  - **rectangular**: Regular grid pattern (orderly)
  - **hexagonal**: Honeycomb hexagonal tiles (geometric)
  - **random**: Organic Voronoi-like shapes (natural)
- `stone_height`: Height of flagstones above base surface in mm (default: 0.3)
- `gap`: Gap between stones for mortar in mm (default: 0.3)
- `stone_size`: Size of stones in mm (for rectangular/hexagonal patterns)
- `num_stones`: Number of stones (for random pattern, default: 30)
- `seed`: Random seed for reproducible patterns

#### `flagstone_base_32mm(pattern="irregular", stone_height=0.3, gap=0.3, stone_size=None, num_stones=35, seed=42)`
Create a 32mm base with flagstone pattern. Same parameters as `flagstone_base_28mm`.

#### `add_flagstone_pattern(base_mesh, radius, base_height, pattern="irregular", ...)`
Add flagstone pattern to any existing base mesh. Useful for decorating custom bases.

### BaseGenerator

#### Methods

- `add_mesh(mesh)`: Add a mesh to the collection
- `combine()`: Combine all meshes into one
- `save(filename)`: Save the combined mesh to a file
- `translate(dx, dy, dz)`: Move all meshes
- `scale(sx, sy, sz)`: Scale all meshes
- `rotate_x/y/z(angle_deg)`: Rotate all meshes around X/Y/Z axis

All transformation methods return `self` for method chaining.

### LLMGenerator

#### `__init__(api_key=None)`
Initialize the LLM generator.

- `api_key`: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)

#### `generate_from_prompt(prompt, filename, model='claude-sonnet-4-5-20250929', execute=True)`
Generate and optionally execute code to create an STL file.

- `prompt`: Natural language description
- `filename`: Output STL filename
- `model`: Claude model to use
- `execute`: Whether to execute the generated code

Returns the generated Python code.

## Examples

Check the `examples/` directory for more examples:

- `basic_shapes.py`: Creating and saving basic shapes
- `miniature_bases.py`: Creating standard 28mm and 32mm miniature bases
- `flagstone_bases.py`: Creating bases with different flagstone patterns
- `combined_shapes.py`: Combining shapes to create complex objects
- `llm_generation.py`: Using Claude to generate STL files from prompts

Run examples:

```bash
uv run python examples/basic_shapes.py
uv run python examples/miniature_bases.py
uv run python examples/flagstone_bases.py
uv run python examples/combined_shapes.py
uv run python examples/llm_generation.py  # Requires ANTHROPIC_API_KEY
```

## Testing

Run tests:

```bash
uv run python tests/test_primitives.py
uv run python tests/test_scenery.py
```

## Project Structure

```
stl-generator/
├── src/
│   └── stl_generator/
│       ├── __init__.py
│       ├── primitives/       # Basic 3D shapes
│       │   ├── __init__.py
│       │   └── shapes.py
│       ├── scenery/         # Base decorations (flagstones, etc.)
│       │   ├── __init__.py
│       │   └── flagstones.py
│       ├── generators/       # Shape composition and transformations
│       │   ├── __init__.py
│       │   └── base.py
│       ├── llm/             # LLM integration
│       │   ├── __init__.py
│       │   └── generator.py
│       └── utils/           # Utility functions
│           ├── __init__.py
│           └── helpers.py
├── examples/                # Example scripts
├── tests/                   # Unit tests
├── pyproject.toml          # Project configuration
└── README.md
```

## Dependencies

- `numpy`: Numerical operations
- `numpy-stl`: STL file manipulation
- `anthropic`: Claude API integration

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
