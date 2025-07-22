from fastapi import FastAPI
from services.copilot import router as copilot_router
from dotenv import load_dotenv
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)

app = FastAPI(
    title="Agent Team API",
    description="API for all agent services",
    version="0.1.0"
)

# CORS configuration
origins = ["*"]  # Adjust this to your frontend's URL(s) for better security

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(copilot_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Agent Team API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
