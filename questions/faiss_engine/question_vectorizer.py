import numpy as np
from .embedder import TextEmbedder
from .faiss_indexer import FAISSIndexer

class QuestionVectorizer:
    """Coordinates DB, FAISS filtering, and cross-encoder reranking with auto-sync."""
    def __init__(self):
        self.embedder = TextEmbedder()
        dim = self.embedder.bi_encoder.get_sentence_embedding_dimension()
        self.indexer = FAISSIndexer(dim=dim)
        self._built = False

    def build(self):
        """Initial full build of the index."""
        from questions.models import Questions
        qs = Questions.objects.all()
        texts = [q.question for q in qs]
        ids = [q.id for q in qs]
        if texts:
            vecs = np.array(self.embedder.encode_bi(texts), dtype='float32')
            self.indexer.add(vecs, ids)
        self._built = True

    def _sync_new(self):
        """Sync any new DB entries not yet in the index."""
        from questions.models import Questions
        all_qs = Questions.objects.all()
        all_ids = {q.id for q in all_qs}
        indexed_ids = set(self.indexer.id_map.values())
        new_ids = all_ids - indexed_ids
        if not new_ids:
            return
        new_qs = [q for q in all_qs if q.id in new_ids]
        texts = [q.question for q in new_qs]
        ids = [q.id for q in new_qs]
        vecs = np.array(self.embedder.encode_bi(texts), dtype='float32')
        self.indexer.add(vecs, ids)

    def query(self, text: str, filter_k: int = 50, rerank_k: int = 5):
        """
        2-stage pipeline:
         1) Build if needed, then sync new entries
         2) FAISS filter + cross-encoder rerank
        """
        if not self._built:
            self.build()
        # Sync DB additions
        self._sync_new()

        # Step 1: filter
        q_vec = np.array(self.embedder.encode_bi([text]), dtype='float32')
        candidates = self.indexer.search(q_vec, top_k=filter_k)

        # Step 2: rerank
        from questions.models import Questions
        cand_list = []
        for qid, _ in candidates:
            try:
                cand_list.append((qid, Questions.objects.get(id=qid).question))
            except Questions.DoesNotExist:
                continue
        reranked = self.embedder.rerank(text, cand_list)
        reranked.sort(key=lambda x: x[2], reverse=True)
        return reranked[:rerank_k]

    def add(self, question_obj):
        """Add single question to index immediately."""
        vec = np.array(self.embedder.encode_bi([question_obj.question]), dtype='float32')
        self.indexer.add(vec, [question_obj.id])

    def rebuild(self):
        """Full rebuild (e.g., on deletion)."""
        dim = self.embedder.bi_encoder.get_sentence_embedding_dimension()
        self.indexer = FAISSIndexer(dim=dim)
        self._built = False
        self.build()

# Singleton instance
_qv = QuestionVectorizer()