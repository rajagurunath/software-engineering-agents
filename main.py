from fastapi import FastAPI
from services.copilot import router as copilot_router
from dotenv import load_dotenv
import uvicorn

load_dotenv(override=True)

app = FastAPI(
    title="Agent Team API",
    description="API for all agent services",
    version="0.1.0"
)

app.include_router(copilot_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Agent Team API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
