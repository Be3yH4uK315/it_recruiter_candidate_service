from fastapi import FastAPI
from app.api.v1.api import api_router
from app.services.publisher import publisher

app = FastAPI(title="Candidate Service")

@app.on_event("startup")
async def startup_event():
    print("Application startup...")
    await publisher.connect()

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown...")
    await publisher.close()

app.include_router(api_router, prefix="/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Candidate Service"}
