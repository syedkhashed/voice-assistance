import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
from io import BytesIO

# Title
st.title("Speech-to-Voice Conversion")

# Step 1: Record user's speech using microphone
def record_audio(duration=5, fs=44100):
    st.write("Recording... Please speak.")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    write('user_audio.wav', fs, audio_data)  # Save as WAV file
    st.write("Recording complete.")
    return 'user_audio.wav'

# Step 2: Convert speech to text
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)  # read the entire audio file
    try:
        text = recognizer.recognize_google(audio)
        st.write(f"Recognized Text: {text}")
        return text
    except sr.UnknownValueError:
        st.write("Google Speech Recognition could not understand the audio.")
        return ""
    except sr.RequestError as e:
        st.write(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

# Step 3: Convert text to speech with different voices
def text_to_speech(text, voice_option):
    # Using gTTS for simplicity
    if text:
        tts = gTTS(text=text, lang='en', tld=voice_option)  # 'tld' for voice variation
        tts.save('converted_speech.mp3')
        st.write("Speech converted into voice.")
        return 'converted_speech.mp3'
    return None

# Step 4: Play back the synthesized speech
def play_audio(file_path):
    audio_file = open(file_path, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

# Main Streamlit UI
st.write("Click the button below to record your speech.")

if st.button("Record"):
    audio_file = record_audio()
    if audio_file:
        # Convert speech to text
        text = speech_to_text(audio_file)

        # Select voice option
        st.write("Select a voice option:")
        voice_option = st.selectbox("Voice", options=["com", "co.uk", "com.au", "co.in", "ca"])

        # Convert text to speech with selected voice
        if text:
            speech_file = text_to_speech(text, voice_option)
            if speech_file:
                st.write("Playing the converted voice...")
                play_audio(speech_file)
