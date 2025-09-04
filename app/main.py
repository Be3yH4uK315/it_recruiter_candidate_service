from fastapi import FastAPI
from .api.v1.api import api_router

app = FastAPI(title="Candidate Service")

app.include_router(api_router, prefix="/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Candidate Service"}