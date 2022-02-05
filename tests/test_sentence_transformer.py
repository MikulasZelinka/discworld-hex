import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")


def test_sentence_transformer_max_length():
    # Max sequence length is 384, due to padding tokens it's 382
    assert np.sum(np.abs(model.encode("Hello " * 1000) - model.encode("Hello " * 381))) > 1e-5
    assert np.sum(np.abs(model.encode("Hello " * 1000) - model.encode("Hello " * 382))) == 0
