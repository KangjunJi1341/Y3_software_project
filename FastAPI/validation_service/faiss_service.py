import json
import numpy as np
import faiss as fs
from sentence_transformers import SentenceTransformer, CrossEncoder
from pathlib import Path

class FaissService:
    def __init__(self, 
                 jsonl_path: str |Path, 
                 text_key:str = "text", 
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 k: int = 5,
                 rerank_model:str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
                 nli_model: str = "cross-encoder/nli-deberta-v3-base"):
        
        self.jsonl_path = Path(jsonl_path)
        self.text_key = text_key
        self.query = None
        self.k = k
        self.model = SentenceTransformer(model_name)
        self.reranker = CrossEncoder(rerank_model)
        self.nli = CrossEncoder(nli_model)
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
    
    def search_semantic(self, query, k, topn = 50, entail_th: float = 0.55):
        if not query:
            raise ValueError("Query is empty")
        
        #FAISS-------------------------------------------------------------------------------------
        query_vectors = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, ids = self.index.search(query_vectors, topn)
        #Cross-Encoder-----------------------------------------------------------------------------
        policy_idx = [int(i) for i in ids[0]]
        policies = [(i, self.texts[i]) for i in policy_idx]
        if not policies:
            raise ValueError("No policies has been found")
        pairs = [(query, text) for _, text in policies]
        scores = self.reranker.predict(pairs)
        reranked = sorted(zip(policies, scores), key=lambda x: x[1], reverse=True)[:k]
        #NLI---------------------------------------------------------------------------------------
        nli_pairs = [(text,query) for (i, text), _ in reranked]

        def batched_predict(model, pairs, batch_size=5, apply_softmax=False):
            out = []
            for j in range(0, len(pairs), batch_size):
                pred = model.predict(pairs[j:j+batch_size], apply_softmax=apply_softmax)
                out.append(pred)
            return np.vstack(out)
        
        nli_probs = batched_predict(self.nli, nli_pairs, apply_softmax=True)
        entail_probs = nli_probs[:, 1]

        final = []
        for (i, text), score, entail_p in zip(policies, scores, entail_probs):
            if entail_p >= entail_th:
                final.append({
                    "id": int(i),
                    "text": text,
                    "rerank_score": float(score),
                    "entail_prob": float(entail_p)
                })

        final = sorted(final, key=lambda x: x["entail_prob"], reverse=True)
        return final