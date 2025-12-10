import faiss_service as FS

svc = FS.FaissService(
    jsonl_path="C:/Users/lenovo/Desktop/SEFB/Group Project/FastAPI/data/imperial_policies.jsonl",
    text_key="text",
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    k=5,
)

query = "late submission will be penalised"
print(f"\nQuery: {query}")

results = svc.search_semantic("late submission will be penalised",k=5)

print(f"\nFound {len(results)} results:\n")
for r in results:
    print(f"[id={r['id']}] (rerank={r['rerank_score']:.3f}, entail={r['entail_prob']:.3f}) {r['text'][:120]}...")
