import streamlit as st
import sounddevice as sd
import numpy as np
import asyncio
import websockets
import json
import os

# Access the API key from Streamlit secrets
deepgram_api_key = "9c5ccd2db18c95a12574e844e2137dd22d33c3e8"

# Initialize Streamlit app
st.title("Live Speech Recording with Deepgram")

# Global variables to manage recording state
is_recording = False
audio_buffer = []

# Function to capture audio
def record_audio(duration):
    global is_recording, audio_buffer
    fs = 16000  # Sample rate
    audio_buffer = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_buffer.append(indata.copy())

    # Start recording
    with sd.InputStream(callback=callback, channels=1, samplerate=fs):
        is_recording = True
        sd.sleep(duration * 1000)  # Duration in milliseconds
        is_recording = False

# Function to transcribe audio
async def transcribe_audio():
    global audio_buffer

    async with websockets.connect(
        f'wss://api.deepgram.com/v1/listen?model=nova&smart_format=true',
        extra_headers={"Authorization": f"Token {deepgram_api_key}"}
    ) as ws:
        # Send audio data to Deepgram
        for audio in audio_buffer:
            # Convert audio to bytes and send
            await ws.send(audio.tobytes())

        # Receive transcription results
        while True:
            response = await ws.recv()
            data = json.loads(response)
            if 'channel' in data and 'alternatives' in data['channel']:
                transcript = data['channel']['alternatives'][0]['transcript']
                if transcript:
                    st.write(transcript)

# Start/stop recording button
if st.button("Start Recording"):
    duration = 10  # Record for 10 seconds (or set your own duration)
    record_audio(duration)
    asyncio.run(transcribe_audio())
