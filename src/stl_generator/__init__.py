"""STL Generator - Generate STL files programmatically or from LLM prompts."""

from stl_generator.primitives import (
    cube,
    sphere,
    cylinder,
    cone,
    miniature_base_28mm,
    miniature_base_32mm,
)
from stl_generator.generators import BaseGenerator
from stl_generator.scenery import (
    add_flagstone_pattern,
    flagstone_base_28mm,
    flagstone_base_32mm,
)

__version__ = "0.1.0"
__all__ = [
    "cube",
    "sphere",
    "cylinder",
    "cone",
    "miniature_base_28mm",
    "miniature_base_32mm",
    "BaseGenerator",
    "LLMGenerator",
    "add_flagstone_pattern",
    "flagstone_base_28mm",
    "flagstone_base_32mm",
]


def __getattr__(name):
    """Lazy import for LLMGenerator to avoid SSL dependency issues."""
    if name == "LLMGenerator":
        from stl_generator.llm import LLMGenerator
        return LLMGenerator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main() -> None:
    """Entry point for the CLI."""
    print("STL Generator v0.1.0")
    print("Generate STL files programmatically or from LLM prompts")
    print("\nUsage:")
    print("  from stl_generator import cube, sphere")
    print("  cube(size=10).save('cube.stl')")
    print("\nSee examples/ directory for more usage examples.")
