import streamlit as st
import requests
import json
import numpy as np
import sounddevice as sd
from audio_recorder_streamlit import audio_recorder
from deepgram import DeepgramClient, SpeakOptions, SpeakWebSocketEvents

# Your API Keys
ASSEMBLYAI_API_KEY = "03aa14046bf74bfe936f6214850443f1"  # Replace with your AssemblyAI API Key
DEEPGRAM_API_KEY = "9c5ccd2db18c95a12574e844e2137dd22d33c3e8"  # Replace with your Deepgram API Key

def transcribe_audio(file):
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/json"
    }
    
    # Upload audio file to AssemblyAI
    upload_response = requests.post("https://api.assemblyai.com/v2/upload", headers=headers, data=file)
    audio_url = upload_response.json().get("upload_url")

    if not audio_url:
        return "Failed to upload audio."

    # Request transcription
    json_data = json.dumps({"audio_url": audio_url})
    transcription_response = requests.post("https://api.assemblyai.com/v2/transcript", headers=headers, data=json_data)
    transcript_id = transcription_response.json().get("id")

    if not transcript_id:
        return "Failed to get transcription ID."

    # Poll for transcription result
    while True:
        response = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        if response.json()["status"] == "completed":
            return response.json()["text"]
        elif response.json()["status"] == "failed":
            return "Sorry, the transcription failed."

def text_to_speech(response):
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        audio_data = []

        # Create a websocket connection to Deepgram
        dg_connection = deepgram.speak.websocket.v("1")

        def on_open(self, open, **kwargs):
            print("WebSocket connection opened.")

        def on_audio_data(data, **kwargs):
            audio_data.append(np.frombuffer(data, dtype=np.int16))  # Collect audio data

        def on_close(self, close, **kwargs):
            print("WebSocket connection closed.")
            if audio_data:
                # Play collected audio data when connection closes
                sd.play(np.concatenate(audio_data), samplerate=48000)
                sd.wait()

        dg_connection.on(SpeakWebSocketEvents.Open, on_open)
        dg_connection.on(SpeakWebSocketEvents.AudioData, on_audio_data)
        dg_connection.on(SpeakWebSocketEvents.Close, on_close)

        # Prepare the options
        options = SpeakOptions(
            model="aura-asteria-en",
            encoding="linear16",
            container="none",
            sample_rate=48000,
        )

        if not dg_connection.start(options):
            print("Failed to start connection")
            return None

        # Send the text to Deepgram
        dg_connection.send_text(response)
        dg_connection.flush()

        # Wait for the audio data to finish writing
        dg_connection.finish()

        return "Audio generation completed."

    except Exception as e:
        st.write(f"An unexpected error occurred during TTS: {e}")
        return None

st.title("🧑‍💻 Talking Assistant")

# Audio recording component
audio_bytes = audio_recorder()
if audio_bytes:
    # Save the Recorded File
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)

    # Transcribe the audio
    with open(audio_location, "rb") as audio_file:
        text = transcribe_audio(audio_file.read())
    st.write("Transcribed Text: ", text)

    if text != "Sorry, the transcription failed.":
        # Generate AI response
        api_response = f"You said: {text}."
        st.write("AI Response: ", api_response)

        # Convert AI response to speech
        result = text_to_speech(api_response)
        if result is not None:
            st.write(result)
        else:
            st.write("Failed to generate audio.")
