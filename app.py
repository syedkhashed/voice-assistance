import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder

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

# Audio recording component
st.write("Click the button to record your voice. Speak clearly into the microphone.")
audio_bytes = audio_recorder(duration=10)  # Set duration to 10 seconds

if audio_bytes:
    # Save the recorded file
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)

    # Confirm that the audio was recorded
    st.write("Audio recorded successfully!")

    # Transcribe the audio
    text = transcribe_audio(audio_location)
    st.write("Transcribed Text: ", text)

    if text and "Sorry" not in text:
        # Generate AI response
        api_response = f"You said: {text}."
        st.write("AI Response: ", api_response)

        # Convert AI response to speech
        speech_file_path = text_to_speech(api_response)
        st.audio(speech_file_path)
    else:
        st.write("Please try again with clearer audio.")
