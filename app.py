import streamlit as st
from audio_recorder_streamlit import audio_recorder
from speech_recognition import Recognizer, AudioFile
from gtts import gTTS
import os

def transcribe_text_to_voice(audio_location):
    recognizer = Recognizer()
    with AudioFile(audio_location) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    return text

def text_to_speech_ai(speech_file_path, api_response):
    tts = gTTS(text=api_response, lang='en')
    tts.save(speech_file_path)

st.title("🧑‍💻 Talking Assistant")

audio_bytes = audio_recorder()
if audio_bytes:
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)

    text = transcribe_text_to_voice(audio_location)
    st.write("Transcribed Text: ", text)

    api_response = "This is a placeholder response based on your input."  # Replace with your AI response logic
    st.write("AI Response: ", api_response)

    speech_file_path = 'audio_response.mp3'
    text_to_speech_ai(speech_file_path, api_response)
    st.audio(speech_file_path)
