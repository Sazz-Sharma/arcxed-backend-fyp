from sentence_transformers import SentenceTransformer, CrossEncoder

class TextEmbedder:
    """Handles bi-encoder and cross-encoder models."""
    def __init__(self,
                 bi_model_name: str = 'all-MiniLM-L12-v2',
                 rerank_model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        # Bi-encoder for vector search
        self.bi_encoder = SentenceTransformer(bi_model_name)
        # Cross-encoder for reranking
        self.reranker = CrossEncoder(rerank_model_name)

    def encode_bi(self, texts, normalize: bool = True):
        return self.bi_encoder.encode(texts, normalize_embeddings=normalize)

    def rerank(self, query: str, candidates: list) -> list:
        # candidates: list of (id, text)
        pairs = [(query, text) for (_id, text) in candidates]
        scores = self.reranker.predict(pairs)
        # Return list of tuples: (id, text, score)
        return [(candidates[i][0], candidates[i][1], float(scores[i]))
                for i in range(len(candidates))]