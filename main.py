import os
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="StoryFlicks Backend API",
    description="Backend API for StoryFlicks application",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("tasks"):
    os.mkdir("tasks")

app.mount("/tasks", StaticFiles(directory=os.path.abspath("tasks")),name="tasks")

app.include_router()

if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=18000, reload=True)