import streamlit as st
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your Deepgram API key from environment variable
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Streamlit UI
st.title("Live Speech Transcription")
status_text = st.empty()
transcript_area = st.empty()
start_button = st.button("Start Recording")
stop_button = st.button("Stop Recording")

# WebSocket connection for transcription
async def transcribe_audio():
    try:
        async with websockets.connect(
            f'wss://api.deepgram.com/v1/listen?access_token={DEEPGRAM_API_KEY}',
        ) as ws:
            # Notify that we are connected
            status_text.text("Connected to Deepgram WebSocket")
            
            while True:
                response = await ws.recv()
                data = json.loads(response)
                
                if 'channel' in data and 'alternatives' in data['channel']:
                    transcript = data['channel']['alternatives'][0]['transcript']
                    if transcript:
                        # Update the transcript area with the new transcript
                        current_transcript = transcript_area.text if transcript_area.text else ""
                        transcript_area.text(f"{current_transcript} {transcript}")
    except Exception as e:
        st.error(f"WebSocket error: {e}")

# Handle button clicks
if start_button:
    status_text.text("Recording...")
    asyncio.run(transcribe_audio())

if stop_button:
    status_text.text("Stopped.")
