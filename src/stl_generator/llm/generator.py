"""LLM-based STL generation using Claude."""

import os
from typing import Optional
from anthropic import Anthropic
from stl import mesh


class LLMGenerator:
    """Generate STL files from natural language prompts using Claude."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM generator.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key or set ANTHROPIC_API_KEY environment variable."
            )
        self.client = Anthropic(api_key=self.api_key)

    def generate_code_from_prompt(self, prompt: str, model: str = "claude-sonnet-4-5-20250929") -> str:
        """
        Generate Python code for STL creation from a natural language prompt.

        Args:
            prompt: Natural language description of the desired 3D object
            model: Claude model to use

        Returns:
            str: Generated Python code
        """
        system_prompt = """You are an expert at generating Python code for creating 3D STL files.

You have access to these functions from stl_generator.primitives:
- cube(size, center=(0,0,0))
- sphere(radius, center=(0,0,0), resolution=20)
- cylinder(radius, height, center=(0,0,0), resolution=32)
- cone(radius, height, center=(0,0,0), resolution=32)

You also have access to BaseGenerator from stl_generator.generators which can:
- add_mesh(mesh) - add a mesh
- combine() - combine all meshes
- save(filename) - save to file
- translate(dx, dy, dz) - move meshes
- scale(sx, sy, sz) - scale meshes
- rotate_x/y/z(angle_deg) - rotate meshes

Generate clean, executable Python code that creates the requested 3D object.
Only output the Python code, no explanations.
The code should be ready to execute and save an STL file."""

        message = self.client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract code from response
        code = message.content[0].text

        # Clean up code blocks if present
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()

        return code

    def generate_from_prompt(self, prompt: str, filename: str,
                            model: str = "claude-sonnet-4-5-20250929",
                            execute: bool = True) -> str:
        """
        Generate and optionally execute code to create an STL file from a prompt.

        Args:
            prompt: Natural language description of the desired 3D object
            filename: Output STL filename
            model: Claude model to use
            execute: Whether to execute the generated code

        Returns:
            str: Generated Python code
        """
        code = self.generate_code_from_prompt(prompt, model)

        if execute:
            # Create a safe execution environment
            exec_globals = {
                "__builtins__": __builtins__,
                "filename": filename,
            }

            # Import required modules into execution environment
            exec("from stl_generator.primitives import cube, sphere, cylinder, cone", exec_globals)
            exec("from stl_generator.generators import BaseGenerator", exec_globals)
            exec("import numpy as np", exec_globals)

            # Execute the generated code
            try:
                exec(code, exec_globals)
                print(f"Successfully generated: {filename}")
            except Exception as e:
                print(f"Error executing generated code: {e}")
                print(f"\nGenerated code:\n{code}")
                raise

        return code
