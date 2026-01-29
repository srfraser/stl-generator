"""Base generator class for creating complex STL objects."""

import numpy as np
from stl import mesh
from typing import List


class BaseGenerator:
    """Base class for STL generators."""

    def __init__(self):
        """Initialize the generator."""
        self.meshes: List[mesh.Mesh] = []

    def add_mesh(self, new_mesh: mesh.Mesh) -> "BaseGenerator":
        """
        Add a mesh to the collection.

        Args:
            new_mesh: Mesh to add

        Returns:
            Self for method chaining
        """
        self.meshes.append(new_mesh)
        return self

    def combine(self) -> mesh.Mesh:
        """
        Combine all meshes into a single mesh.

        Returns:
            mesh.Mesh: Combined mesh
        """
        if not self.meshes:
            raise ValueError("No meshes to combine")

        if len(self.meshes) == 1:
            return self.meshes[0]

        # Calculate total number of faces
        total_faces = sum(m.data.size for m in self.meshes)

        # Create combined mesh
        combined = mesh.Mesh(np.zeros(total_faces, dtype=mesh.Mesh.dtype))

        # Copy all faces
        offset = 0
        for m in self.meshes:
            face_count = m.data.size
            combined.data[offset:offset + face_count] = m.data
            offset += face_count

        return combined

    def save(self, filename: str) -> None:
        """
        Save the combined mesh to a file.

        Args:
            filename: Output filename (should end with .stl)
        """
        combined = self.combine()
        combined.save(filename)
        print(f"Saved STL file: {filename}")

    def translate(self, dx: float = 0, dy: float = 0, dz: float = 0) -> "BaseGenerator":
        """
        Translate all meshes.

        Args:
            dx: X translation
            dy: Y translation
            dz: Z translation

        Returns:
            Self for method chaining
        """
        translation = np.array([dx, dy, dz])
        for m in self.meshes:
            m.vectors += translation
        return self

    def scale(self, sx: float = 1.0, sy: float = 1.0, sz: float = 1.0) -> "BaseGenerator":
        """
        Scale all meshes.

        Args:
            sx: X scale factor
            sy: Y scale factor
            sz: Z scale factor

        Returns:
            Self for method chaining
        """
        scale_vector = np.array([sx, sy, sz])
        for m in self.meshes:
            m.vectors *= scale_vector
        return self

    def rotate_x(self, angle_deg: float) -> "BaseGenerator":
        """
        Rotate all meshes around X axis.

        Args:
            angle_deg: Rotation angle in degrees

        Returns:
            Self for method chaining
        """
        angle_rad = np.radians(angle_deg)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

        rotation_matrix = np.array([
            [1, 0, 0],
            [0, cos_a, -sin_a],
            [0, sin_a, cos_a]
        ])

        for m in self.meshes:
            for i in range(len(m.vectors)):
                for j in range(3):
                    m.vectors[i][j] = rotation_matrix @ m.vectors[i][j]

        return self

    def rotate_y(self, angle_deg: float) -> "BaseGenerator":
        """
        Rotate all meshes around Y axis.

        Args:
            angle_deg: Rotation angle in degrees

        Returns:
            Self for method chaining
        """
        angle_rad = np.radians(angle_deg)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

        rotation_matrix = np.array([
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a]
        ])

        for m in self.meshes:
            for i in range(len(m.vectors)):
                for j in range(3):
                    m.vectors[i][j] = rotation_matrix @ m.vectors[i][j]

        return self

    def rotate_z(self, angle_deg: float) -> "BaseGenerator":
        """
        Rotate all meshes around Z axis.

        Args:
            angle_deg: Rotation angle in degrees

        Returns:
            Self for method chaining
        """
        angle_rad = np.radians(angle_deg)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

        rotation_matrix = np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ])

        for m in self.meshes:
            for i in range(len(m.vectors)):
                for j in range(3):
                    m.vectors[i][j] = rotation_matrix @ m.vectors[i][j]

        return self
