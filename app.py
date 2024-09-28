import streamlit as st
import requests
import json
from audio_recorder_streamlit import audio_recorder
from deepgram import DeepgramClient, SpeakOptions, SpeakWebSocketEvents

DEEPGRAM_API_KEY = "9c5ccd2db18c95a12574e844e2137dd22d33c3e8"  # Your Deepgram API Key

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
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        
        # Create a websocket connection to Deepgram
        dg_connection = deepgram.speak.websocket.v("1")

        audio_file_path = "response.wav"

        # Open the audio file for writing
        with open(audio_file_path, "wb") as audio_file:
            def on_audio_data(data, **kwargs):
                audio_file.write(data)  # Write the audio data to the file

            dg_connection.on(SpeakWebSocketEvents.AudioData, on_audio_data)

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

        return audio_file_path

    except Exception as e:
        print(f"An unexpected error occurred during TTS: {e}")
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
        # Generate AI response (placeholder)
        api_response = f"You said: {text}."
        st.write("AI Response: ", api_response)

        # Convert AI response to speech
        speech_file_path = text_to_speech(api_response)
        if speech_file_path:
            st.audio(speech_file_path)  # Play the audio
