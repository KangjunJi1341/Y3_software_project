from fastapi import FastAPI
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

app = FastAPI()

class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers['X-Total-Process-Time'] = f"{process_time:.5f}s"
        print(f"[LOG] {request.url.path} took {process_time:.5f}s")
        return response
    
app.add_middleware(MyMiddleware)

@app.get("/")
async def root():
    return {"Status":"OK"}