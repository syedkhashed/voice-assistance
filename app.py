import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import os

def convert_to_wav(input_file):
    # Convert audio file to WAV format
    audio = AudioSegment.from_file(input_file)
    wav_file = "converted_audio.wav"
    audio.export(wav_file, format="wav")
    return wav_file

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
    # Save the uploaded file temporarily
    temp_file_path = "uploaded_audio.mp3"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Convert the uploaded file to WAV format if it's not already
    if uploaded_file.type == "audio/mpeg":  # Check if it's an MP3 file
        wav_file_path = convert_to_wav(temp_file_path)
    else:
        wav_file_path = "uploaded_audio.wav"
        with open(wav_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # Transcribe the saved file to text
    text = transcribe_audio(wav_file_path)
    st.write("Transcribed Text: ", text)

    # Replace this with your own AI response logic
    api_response = "This is a placeholder response based on your input."
    st.write("AI Response: ", api_response)

    # Read out the text response using tts
    speech_file_path = text_to_speech(api_response)
    st.audio(speech_file_path)
