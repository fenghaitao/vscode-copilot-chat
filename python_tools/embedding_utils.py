"""
Utilities for handling embeddings from the Copilot Chat index.
Based on: src/platform/embeddings/common/embeddingsStorage.ts
"""

import struct
import numpy as np
from typing import Tuple


def unpack_embedding(data: bytes, embedding_model: str) -> np.ndarray:
    """
    Unpack binary embedding data based on the model type.

    Args:
        data: Raw bytes from the database
        embedding_model: Model identifier (e.g., 'text-embedding-3-small-512', 'metis-1024-I16-Binary')

    Returns:
        NumPy array of embedding values
    """
    if embedding_model == "metis-1024-I16-Binary":
        # Binary quantized embeddings
        if len(data) < 128:  # 1024 bits = 128 bytes
            # Unpack from binary representation
            values = []
            for byte in data:
                for j in range(8):
                    # Each bit represents a binary value
                    values.append(0.03125 if (byte & (1 << j)) else -0.03125)
            return np.array(values, dtype=np.float32)

    # Default: float32 embeddings (text-embedding-3-small-512 and others)
    num_floats = len(data) // 4
    return np.array(struct.unpack(f'{num_floats}f', data), dtype=np.float32)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns:
        Similarity score between -1 and 1 (1 = identical direction)
    """
    dot_product = np.dot(vec1, vec2)
    norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)

    if norm_product == 0:
        return 0.0

    return float(dot_product / norm_product)

def pack_embedding_vector(embedding: list, embedding_model: str) -> bytes:
    """
    Pack an embedding vector into bytes for storage.

    Args:
        embedding: List of floats representing the embedding
        embedding_model: Model identifier

    Returns:
        Packed bytes
    """
    import struct

    if embedding_model == "metis-1024-I16-Binary":
        # Pack as binary
        if len(embedding) % 8 != 0:
            raise ValueError(f"Binary embedding length must be multiple of 8, got {len(embedding)}")

        data = bytearray(len(embedding) // 8)
        for i in range(0, len(embedding), 8):
            value = 0
            for j in range(8):
                value |= (1 if embedding[i + j] >= 0 else 0) << j
            data[i // 8] = value
        return bytes(data)

    # Default: float32
    return struct.pack(f'{len(embedding)}f', *embedding)

def get_embedding_info(embedding_model: str) -> dict:
    """
    Get metadata about an embedding model.

    Returns:
        Dictionary with model information
    """
    models = {
        "text-embedding-3-small-512": {
            "provider": "OpenAI",
            "dimensions": 512,
            "quantization": "float32",
            "size_bytes": 2048  # 512 * 4 bytes
        },
        "metis-1024-I16-Binary": {
            "provider": "GitHub",
            "dimensions": 1024,
            "quantization": "binary",
            "size_bytes": 128  # 1024 bits / 8
        }
    }

    return models.get(embedding_model, {
        "provider": "Unknown",
        "dimensions": "Unknown",
        "quantization": "float32",
        "size_bytes": "Unknown"
    })
