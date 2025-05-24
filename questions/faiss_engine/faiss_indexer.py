import faiss
import numpy as np

class FAISSIndexer:
    """Manages FAISS index for fast vector retrieval."""
    def __init__(self, dim: int = 384):
        self.index = faiss.IndexFlatIP(dim)
        self.id_map = {}  # maps index positions --> database IDs

    def add(self, vectors: np.ndarray, ids: list):
        """Add vectors and map their positions to DB IDs."""
        assert vectors.ndim == 2 and len(ids) == vectors.shape[0]
        self.index.add(vectors)
        base = self.index.ntotal - vectors.shape[0]
        for i, db_id in enumerate(ids):
            self.id_map[base + i] = db_id

    def remove(self, db_id: int):
        """FAISS Flat indexes do not support removal. Must rebuild entire index."""
        # Flag for rebuild
        raise NotImplementedError("Removal not supported; rebuild index on delete.")

    def search(self, vector: np.ndarray, top_k: int = 5):
        scores, indices = self.index.search(vector, top_k)
        # returns list of tuples: (db_id, score)
        results = []
        for idx, score in zip(indices[0], scores[0]):
            db_id = self.id_map.get(idx)
            if db_id is not None:
                results.append((db_id, float(score)))
        return results

    def save(self, path: str):
        faiss.write_index(self.index, path)

    def load(self, path: str):
        self.index = faiss.read_index(path)
