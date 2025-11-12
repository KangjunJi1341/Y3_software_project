import json
import numpy as np
import faiss as fs
from sentence_transformers import SentenceTransformer
from pathlib import Path

class FaissService:
    def __init__(self, 
                 jsonl_path: str |Path, 
                 text_key:str = "text", 
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 k: int = 5):
        
        self.jsonl_path = Path(jsonl_path)
        self.text_key = text_key
        self.query = None
        self.k = k
        self.model = SentenceTransformer(model_name)
        self.items, self.texts = self.load_sentences(self.jsonl_path, self.text_key)
        self.index, self.vector = self.build_index(self.texts)
        self.results = []

    def load_sentences(self, jsonl_path, text_key="text"):
        items, texts = [], []
        with open(jsonl_path,'r',encoding='utf-8') as f:
            for ln, line in enumerate(f, 1):

                try:
                    data = json.loads(line.strip())
                except json.JSONDecodeError as e:
                    print(f"[Warning] Line {ln} not a valid jsonl: {e}")
                    continue

                if not data or text_key not in data or not data[text_key]:
                    print(f"[Warning] Line {ln} missing '{text_key}'")
                    continue

                items.append(data)
                texts.append(data[text_key])        
        return items, texts    

    def build_index(self, texts):
        vector = self.model.encode(texts, normalize_embeddings=True).astype("float32")
        vector = np.ascontiguousarray(vector, dtype='float32')
        index = fs.IndexFlatIP(vector.shape[1])
        index.add(vector)
        return index, vector

    def search(self, query , k):
        if not query:
            raise ValueError("Query is empty.")      
        self.query = query
        k = k

        query_vectors = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, ids = self.index.search(query_vectors, k)
        results = []
        
        for rank, (i, s) in enumerate(zip(ids[0], scores[0]), 1):
            i = int(i)
            results.append({
                "rank": rank, 
                "score": float(s), 
                "text": self.texts[i], 
                "id": i})
        return results