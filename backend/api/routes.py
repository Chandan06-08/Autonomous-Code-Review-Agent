from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
from ..workflows.orchestration import Orchestrator

app = FastAPI(title="Autonomous Code Review Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

class IssueRequest(BaseModel):
    issue_url: str

@app.post("/api/submit")
async def submit_issue(request: IssueRequest, background_tasks: BackgroundTasks):
    # Start the orchestrator in the background
    background_tasks.add_task(orchestrator.run, request.issue_url)
    return {"status": "started", "message": "Agent workflow initiated."}

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    last_log_count = 0
    try:
        while True:
            # Check for new logs
            current_logs = orchestrator.logs
            if len(current_logs) > last_log_count:
                new_logs = current_logs[last_log_count:]
                for log in new_logs:
                    await websocket.send_text(json.dumps(log))
                last_log_count = len(current_logs)
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"WebSocket closed: {e}")
    finally:
        await websocket.close()

@app.get("/api/status")
async def get_status():
    return {"logs": orchestrator.logs}

# Mount static files LAST to ensure API routes are handled first
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
