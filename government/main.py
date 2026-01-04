from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from government import duckduckgo_scheme_search
import whisper
import os
import tempfile

app = FastAPI(title="Government Scheme Finder API")

# Load Whisper model (base is good for multilingual speed)
model = whisper.load_model("base")

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserProfile(BaseModel):
    age: str
    gender: str
    state: str
    income_bracket: str
    occupation: str
    category: str

@app.post("/find-schemes")
def find_schemes(user: UserProfile):
    schemes = duckduckgo_scheme_search(user.dict())

    return {
        "query_state": user.state,
        "count": len(schemes),
        "schemes": schemes,
        "disclaimer": "Final eligibility is determined by the concerned government department."
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Transcribe using Whisper
        result = model.transcribe(tmp_path)
        return {"text": result["text"]}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
