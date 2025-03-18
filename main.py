from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from AgentWorkflow.graph import run_transcriber
import logging
import os

# Initialize FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request Model
class SummaryRequest(BaseModel):
    video_name: str

# Response Model
class SummaryResponse(BaseModel):
    summary: str | None
    key_points: str | None
    video_url: str | None
    issue: str | None = None

@app.post('/get_summary', response_model=SummaryResponse)
async def get_summary(request: SummaryRequest):
    """
    Fetches a YouTube video transcript, generates a summary and key points.

    Returns:
        - `summary`: The summarized video content.
        - `key_points`: 5 key points from the video.
        - `video_url`: The actual YouTube video URL.
        - `issue`: Describes any issue encountered.
    """
    try:
        result = await run_transcriber(video_name=request.video_name)
        
        issue = None
        if not result.get("transcript"):
            issue = "Video does not support transcription"
            logger.warning(f"Transcription failed for {request.video_name}")
            raise HTTPException(status_code=422, detail="Video does not support transcription")
        
        return {
            "summary": result.get("summary"),
            "key_points": result.get("key_points"),
            "video_url": result.get("url"),
            "issue": issue
        }

    except Exception as e:
        logger.error(f"Error processing video '{request.video_name}': {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.get("/get_audio")
async def get_audio():
    """
    Endpoint to serve the generated audio file.
    """
    file_path = "summary.mp3"  

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(file_path, media_type="audio/mpeg", filename=file_path)


@app.get("/")
async def root():
    return {"message": "Welcome to the Agentic Email Summarizer API!😶‍🌫️"}