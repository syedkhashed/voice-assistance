import streamlit as st
import requests
import json
import pyttsx3
from audio_recorder_streamlit import audio_recorder

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def transcribe_audio(file):
    headers = {
        "authorization": "03aa14046bf74bfe936f6214850443f1",  # Your AssemblyAI API Key
        "content-type": "application/json"
    }
    
    # Upload audio file to AssemblyAI
    upload_response = requests.post("https://api.assemblyai.com/v2/upload", headers=headers, data=file)
    audio_url = upload_response.json()["upload_url"]

    # Request transcription
    json_data = json.dumps({"audio_url": audio_url})
    transcription_response = requests.post("https://api.assemblyai.com/v2/transcript", headers=headers, data=json_data)
    transcript_id = transcription_response.json()["id"]

    # Poll for transcription result
    while True:
        response = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        if response.json()["status"] == "completed":
            return response.json()["text"]
        elif response.json()["status"] == "failed":
            return "Sorry, the transcription failed."

def text_to_speech(response):
    audio_file_path = "response.mp3"
    engine.save_to_file(response, audio_file_path)
    engine.runAndWait()
    return audio_file_path

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
        # Generate AI response (placeholder)
        api_response = f"You said: {text}."
        st.write("AI Response: ", api_response)

        # Convert AI response to speech
        speech_file_path = text_to_speech(api_response)
        st.audio(speech_file_path)
