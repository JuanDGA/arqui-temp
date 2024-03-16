import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI

import routes.document_router
import services.documents


@asynccontextmanager
async def initialize(_: FastAPI):
    # Start Up
    thread = threading.Thread(target=services.documents.documents_processor)
    thread.start()
    yield
    # Shutdown
    services.documents.stop()
    thread.join()


app = FastAPI(lifespan=initialize)
app.include_router(routes.document_router.router)


@app.get("/")
async def root():
    return {"version": "0.0.1v"}

