

import streamlit as st
import asyncio
import websockets
import json
import os

deepgram_api_key = "9c5ccd2db18c95a12574e844e2137dd22d33c3e8"

# Function to transcribe audio using Deepgram API
async def transcribe_audio(audio_data):
    async with websockets.connect(
        f'wss://api.deepgram.com/v1/listen?model=nova&smart_format=true',
        extra_headers={"Authorization": f"Token {deepgram_api_key}"}
    ) as ws:
        await ws.send(audio_data)

        while True:
            response = await ws.recv()
            data = json.loads(response)
            if 'channel' in data and 'alternatives' in data['channel']:
                transcript = data['channel']['alternatives'][0]['transcript']
                if transcript:
                    st.write(transcript)

# Streamlit UI
st.title("Live Speech Recording with Deepgram")

# JavaScript for audio recording
js_code = """
<script>
let mediaRecorder;
let audioChunks = [];

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const reader = new FileReader();
        reader.onload = async () => {
            const audioData = reader.result.split(',')[1];
            await fetch('/transcribe', {
                method: 'POST',
                body: JSON.stringify({ audio: audioData }),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        };
        reader.readAsDataURL(audioBlob);
    };
}

function stopRecording() {
    mediaRecorder.stop();
}

document.getElementById('start').onclick = startRecording;
document.getElementById('stop').onclick = stopRecording;
</script>
<button id="start">Start Recording</button>
<button id="stop">Stop Recording</button>
"""

# Render the JavaScript in Streamlit
st.components.v1.html(js_code)

# Streamlit route to handle audio transcription
if st.button("Start Transcription"):
    audio_data = st.text_area("Paste your audio data here (Base64):")
    if audio_data:
        asyncio.run(transcribe_audio(audio_data))
