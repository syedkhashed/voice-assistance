import os
import streamlit as st
from deepgram import Deepgram
import asyncio
from dotenv import load_dotenv



deepgram_api_key="9c5ccd2db18c95a12574e844e2137dd22d33c3e8"
# Load environment variables from .env file
try:    
    deepgram_client = Deepgram(deepgram_api_key)
except Exception as e:    
    st.error(f"Error initializing Deepgram client: {e}")




# Streamlit layout
st.title("Audio Transcription with Deepgram")
st.write("Upload an audio file (WAV format):")

# Placeholder for displaying the transcription
transcription_placeholder = st.empty()

uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with open("temp_audio.wav", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    async def transcribe_audio(file_path):
        """Transcribe the uploaded audio using Deepgram."""
        with open(file_path, 'rb') as audio_file:
            source = {'buffer': audio_file, 'mimetype': 'audio/wav'}
            response = await deepgram_client.transcription.pre_recorded(source, {'punctuate': True})
            return response['channel']['alternatives'][0]['transcript']

    # Use asyncio to handle the transcription
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    transcription = loop.run_until_complete(transcribe_audio("temp_audio.wav"))
    transcription_placeholder.write("Transcription:")
    transcription_placeholder.write(transcription)
