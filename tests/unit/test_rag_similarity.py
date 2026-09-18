import pytest

from job_analysis.rag.similarity import cosine_similarity

def test_cosine_similarity():
    question_vectors = [1.0,0.0]
    vector_a = [10.0,0.0]
    vector_b = [0.7,0.7]
    similarity_a = cosine_similarity(question_vectors, vector_a)
    similarity_b = cosine_similarity(question_vectors, vector_b)
    assert pytest.approx(similarity_a) == 1.0
    assert pytest.approx(similarity_b) == 0.70710678
    assert similarity_a > similarity_b