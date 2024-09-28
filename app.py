import streamlit as st
import speech_recognition as sr
from gtts import gTTS

def transcribe_audio(file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return f"API request failed with error: {e}"

def text_to_speech(response):
    tts = gTTS(text=response, lang='en')
    tts_file = 'response.mp3'
    tts.save(tts_file)
    return tts_file

st.title("🧑‍💻 Talking Assistant")

uploaded_file = st.file_uploader("Upload a WAV audio file", type=["wav"])

if uploaded_file is not None:
    # Save the uploaded WAV file
    wav_file_path = "uploaded_audio.wav"
    with open(wav_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Transcribe the audio
    text = transcribe_audio(wav_file_path)
    st.write("Transcribed Text: ", text)

    if text != "Sorry, I could not understand the audio.":
        # Generate AI response (placeholder)
        api_response = f"You said: {text}.?"
        st.write("AI Response: ", api_response)

        # Convert AI response to speech
        speech_file_path = text_to_speech(api_response)
        st.audio(speech_file_path)
