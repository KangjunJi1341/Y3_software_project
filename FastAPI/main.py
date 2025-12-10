from fastapi import FastAPI, HTTPException, Request,status
from fastapi.middleware.cors import CORSMiddleware
import time
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from validation_service.faiss_service import FaissService
import os, logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import BaseModel

class HealthCheck(BaseModel):
    status:str = "OK"
    ok:bool
    model:str

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Set Environment Variables---------------------------------------------------------

DATA_PATH = os.getenv("DATA_PATH","data/imperial_policies.jsonl")
TEXT_KEY = os.getenv("TEXT_KEY","text")
MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
K = int(os.getenv("K", "5"))
print(f"Using data from: {DATA_PATH}")

#LifeSpan---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app:FastAPI):
    startup_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"[Start Up] {startup_time}")

        app.state.config = {
        "jsonl_path":DATA_PATH,
        "model_name":MODEL_NAME,
        "k":K
        }

        app.state.svc = FaissService(
        jsonl_path=DATA_PATH,
        text_key=TEXT_KEY,
        model_name=MODEL_NAME,
        k=K
        )

        scheduler = AsyncIOScheduler(timezone = "UTC")

        async def housekeeping():
            logger.info("housekeeping tick")

        scheduler.add_job(
        housekeeping, "interval", minutes=5,
        id="housekeeping",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
        replace_existing=True,
        )

        scheduler.start()
        app.state.scheduler = scheduler

        yield

    except Exception as e:
        logger.exception("Start Up failed")
        raise

    finally:
      if scheduler:
        scheduler.shutdown(wait=False)
        shutdown_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        logger.info(f"[Shut down], {shutdown_time}")

#MainApplication--------------------------------------------------------------------
app = FastAPI(title = "Policy Vector Search", lifespan = lifespan)

class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers['X-Total-Process-Time'] = f"{process_time:.5f}s"
        print(f"[LOG] {request.url.path} took {process_time:.5f}s")
        return response

origins = ["http://localhost:8000", "http://localhost:3000"]

app.add_middleware(MyMiddleware)
app.add_middleware(CORSMiddleware, 
                   allow_origins = origins,
                   allow_credentials = True,
                   allow_methods = ["*"],
                   allow_headers = ["*"])

@app.get("/health", tags = ["healthcheck"],
         summary = "Perform a Health Check",
        response_description = "Return HTTP 200 (OK)",
        status_code = status.HTTP_200_OK,
        response_model = HealthCheck)

def health(request: Request):
    ok = hasattr(request.app.state, "svc")
    return {"ok": ok, "model": request.app.state.config["model_name"]}

@app.get("/search")
def search(q: str, k: int | None = None, request: Request = None):
    cfg = request.app.state.config
    svc = request.app.state.svc
    topk = min(max(1, k or cfg["k"]),20)
    if not q.strip():
        raise HTTPException(status_code = 400,detail = "Query parameter is empty.")
    return {"query": q, "results":svc.search(q, k = topk)}