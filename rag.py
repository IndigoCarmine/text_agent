from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np

def find_similar_terms(text: str, terms: List[Dict], threshold: float = 0.7) -> List[str]:
    """Convenience function for one-off similarity search."""
    rag = TerminologyRAG(terms)
    return rag.search(text, threshold) or []
# rag.py
"""
RAG (Retrieval-Augmented Generation) for terminology context.
Loads terminology from JSON, computes embeddings, and searches with FAISS.
"""


class TerminologyRAG:
    def __init__(self, terms: List[Dict[str, Any]], model_name: str = 'all-MiniLM-L6-v2'):
        self.terms = terms
        self.model = SentenceTransformer(model_name)
        self.term_texts = [t['term'] for t in terms]
        self.embeddings = self.model.encode(self.term_texts, show_progress_bar=False)
        self.nn = NearestNeighbors(metric='cosine')
        self.nn.fit(self.embeddings)

    def search(self, text: str, threshold: float = 0.7) -> List[str]:
        query_emb = self.model.encode([text])
        distances, indices = self.nn.kneighbors(query_emb, n_neighbors=len(self.terms))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            sim = 1 - dist  # cosine距離→類似度
            if sim >= threshold:
                results.append(self.term_texts[idx])
        return results
