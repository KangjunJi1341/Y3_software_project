import faiss_service as FS

svc = FS.FaissService("C:/Users/lenovo/Desktop/SEFB/Group Project/FastAPI/data/imperial_policies.jsonl")

results = svc.search("late submission penalty", k=5)

for r in results:
    print(f"[{r['rank']}] (score={r['score']:.3f}) {r['text']}")

