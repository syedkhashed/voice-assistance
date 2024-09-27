import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os

def transcribe_audio(file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)

def text_to_speech(response):
    tts = gTTS(text=response, lang='en')
    tts_file = 'response.mp3'
    tts.save(tts_file)
    return tts_file

st.title("🧑‍💻 Talking Assistant")

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])

if uploaded_file is not None:
    with open("uploaded_audio.wav", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    text = transcribe_audio("uploaded_audio.wav")
    st.write("Transcribed Text: ", text)

    # Replace this with your own AI response logic
    api_response = "This is a placeholder response based on your input."
    st.write("AI Response: ", api_response)

    speech_file_path = text_to_speech(api_response)
    st.audio(speech_file_path)
