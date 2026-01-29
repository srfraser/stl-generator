"""Example: Generate STL files from natural language prompts using Claude."""

import os
from stl_generator.llm import LLMGenerator

# Check for API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY environment variable not set")
    print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
    exit(1)

# Initialize the LLM generator
generator = LLMGenerator()

# Example prompts
prompts = [
    "Create a simple house with a cube base and a triangular roof using a cone",
    "Make a tower using three cylinders stacked on top of each other with decreasing radius",
    "Create a dumbbell using two spheres connected by a cylinder",
]

print("Generating STL files from prompts...\n")

for i, prompt in enumerate(prompts, 1):
    print(f"Prompt {i}: {prompt}")
    try:
        # Generate and save the STL file
        code = generator.generate_from_prompt(
            prompt=prompt,
            filename=f"output_llm_{i}.stl",
            execute=True
        )
        print(f"Generated code:\n{code}\n")
        print("-" * 80 + "\n")
    except Exception as e:
        print(f"Failed to generate: {e}\n")

print("LLM generation examples completed!")
