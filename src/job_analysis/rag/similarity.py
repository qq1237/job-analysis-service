from math import sqrt


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "vectors must have the same dimension"
        )

    if not vector_a:
        raise ValueError("vectors must not be empty")

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sqrt(
        sum(value * value for value in vector_a)
    )
    magnitude_b = sqrt(
        sum(value * value for value in vector_b)
    )

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        raise ValueError("vectors must not be zero vectors")

    return dot_product / (magnitude_a * magnitude_b)