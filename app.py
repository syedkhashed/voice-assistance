# speech_to_ai_speech.py

import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import pyttsx3
from pydub import AudioSegment
import os

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to transcribe audio to text
def transcribe_audio_to_text(audio_location):
    recognizer = sr.Recognizer()
    
    # Load the audio file and convert it to a format compatible with speech recognition
    audio = AudioSegment.from_wav(audio_location)
    audio.export("temp.wav", format="wav")
    
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    return text

# Function to convert text to speech
def text_to_speech_ai(response):
    engine.save_to_file(response, 'audio_response.mp3')
    engine.runAndWait()

# Streamlit app setup
st.title("🗣️ Speech to AI Speech Assistant")

"""
Hi! Just click on the voice recorder and let me know how I can assist you today?
"""

audio_bytes = audio_recorder()
if audio_bytes:
    # Save the recorded audio file
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)

    # Transcribe the saved audio file to text
    text = transcribe_audio_to_text(audio_location)
    st.write("You said:", text)

    # Create a simple AI response (for demonstration purposes)
    api_response = f"You said: {text}. How can I assist you further?"
    st.write("AI response:", api_response)

    # Convert AI response to speech and play it
    text_to_speech_ai(api_response)
    st.audio('audio_response.mp3')

# Clean up temporary files
if os.path.exists("temp.wav"):
    os.remove("temp.wav")
