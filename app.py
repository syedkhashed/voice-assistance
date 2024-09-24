import os
import streamlit as st
import pyaudio
import wave
import numpy as np
from deepgram import Deepgram
import asyncio
import dotenv

dotenv.load_dotenv()

# Initialize Deepgram client
deepgram_client = Deepgram(os.getenv('DEEPGRAM_API_KEY'))

# Streamlit layout
st.title("Live Audio Transcription with Deepgram")
st.write("Press the button below to start recording:")

# Placeholder for displaying the transcription
transcription_placeholder = st.empty()

def record_audio(seconds=5):
    """Record audio for a specified duration."""
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    st.write("Recording...")
    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    st.write("Recording complete.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the audio to a temporary file
    wave_file = "temp_audio.wav"
    with wave.open(wave_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return wave_file

async def transcribe_audio(file_path):
    """Transcribe the recorded audio using Deepgram."""
    with open(file_path, 'rb') as audio_file:
        source = {'buffer': audio_file, 'mimetype': 'audio/wav'}
        response = await deepgram_client.transcription.pre_recorded(source, {'punctuate': True})
        return response['channel']['alternatives'][0]['transcript']

if st.button("Record"):
    audio_file_path = record_audio(seconds=5)  # Record for 5 seconds
    # Use asyncio to handle the transcription
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    transcription = loop.run_until_complete(transcribe_audio(audio_file_path))
    transcription_placeholder.write("Transcription:")
    transcription_placeholder.write(transcription)

