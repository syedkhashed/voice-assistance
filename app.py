import os
import streamlit as st
from pydub import AudioSegment
import speech_recognition as sr
import io

# Set the path for ffmpeg
# This will append the bin directory to the PATH environment variable
ffmpeg_path = os.path.join(os.getcwd(), 'bin')  # Adjust path to 'bin' folder
os.environ["PATH"] += os.pathsep + ffmpeg_path

# Title of the app
st.title("Speech to Text with Audio Playback")

# Upload an audio file
audio_file = st.file_uploader("Upload an audio file (MP3 or WAV)", type=["mp3", "wav"])

if audio_file:
    # Display uploaded audio file
    st.audio(audio_file, format='audio/mp3')

    # Convert the uploaded audio to an AudioSegment for playback
    audio = AudioSegment.from_file(audio_file)

    # Save the file temporarily in memory
    audio_data = io.BytesIO()
    audio.export(audio_data, format="wav")  # Export to .wav for speech recognition
    audio_data.seek(0)

    # Perform speech recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio_content = recognizer.record(source)  # Record the audio content
        try:
            # Recognize the speech using Google's API
            text = recognizer.recognize_google(audio_content)
            st.write("Transcribed Text: ")
            st.success(text)  # Display the recognized text
        except sr.UnknownValueError:
            st.error("Could not understand the audio")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
