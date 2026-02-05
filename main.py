import base64
import os
import json
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# 1. LOAD YOUR SECRETS [cite: 31]
load_dotenv()
# Make sure your .env file has: GOOGLE_API_KEY=your_key_here
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()

# 2. DEFINE THE INPUT FORMAT (As per Problem Statement) [cite: 45, 46]
class VoiceRequest(BaseModel):
    language: str      # Tamil, English, Hindi, Malayalam, Telugu [cite: 49]
    audioFormat: str   # Always mp3 [cite: 51]
    audioBase64: str   # The encoded audio data [cite: 53]

# 3. THE API ENDPOINT
@app.post("/api/voice-detection")
async def detect_voice(data: VoiceRequest, x_api_key: str = Header(None)):
    
    # Security check for the mandatory header [cite: 29, 31, 32]
    if x_api_key != "sk_test_123456789": 
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # Convert Base64 text to raw audio bytes [cite: 25]
        audio_bytes = base64.b64decode(data.audioBase64)
        
        # SYSTEM INSTRUCTION: Tells the AI how to act and what to return [cite: 71, 75]
        sys_instruct = (
            "You are an expert audio forensic analyst. Analyze the provided audio. "
            "Determine if it is 'HUMAN' or 'AI_GENERATED'. "
            "Respond ONLY in valid JSON with these fields: status, language, classification, "
            "confidenceScore (0.0 to 1.0), and explanation."
        )

        # 4. CALL THE NEW GEMINI CLIENT
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            config={
                "system_instruction": sys_instruct,
                "response_mime_type": "application/json" # Forces JSON output [cite: 21]
            },
            contents=[
                f"Analyze this {data.language} audio file.",
                {"mime_type": "audio/mp3", "data": audio_bytes}
            ]
        )

        # Parse and return the AI's JSON decision [cite: 56, 91]
        return json.loads(response.text)

    except Exception as e:
        # Error handling as per requirement [cite: 82, 85]
        return {"status": "error", "message": str(e)}

# TO RUN: uvicorn main:app --reload