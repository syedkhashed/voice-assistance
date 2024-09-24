import os
import time
import requests
import subprocess
import streamlit as st
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

# Set your API keys directly
DEEPGRAM_API_KEY = "9c5ccd2db18c95a12574e844e2137dd22d33c3e8"
GROQ_API_KEY = "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"

# Initialize Deepgram and Groq clients
deepgram_client = DeepgramClient(DEEPGRAM_API_KEY)
llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768", groq_api_key=GROQ_API_KEY)

# Memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Load the system prompt from a file
with open('system_prompt.txt', 'r') as file:
    system_prompt = file.read().strip()

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{text}")
])

conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)

class TranscriptCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)

transcript_collector = TranscriptCollector()

async def get_transcript(callback):
    transcription_complete = asyncio.Event()

    try:
        # Configure Deepgram connection
        dg_connection = deepgram_client.listen.asynclive.v("1")
        print("Listening...")

        async def on_message(result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                if len(full_sentence.strip()) > 0:
                    print(f"Human: {full_sentence}")
                    callback(full_sentence)
                    transcript_collector.reset()
                    transcription_complete.set()

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=300,
            smart_format=True,
        )

        await dg_connection.start(options)

        # Open a microphone stream
        microphone = Microphone(dg_connection.send)
        microphone.start()

        await transcription_complete.wait()  # Wait for transcription to complete
        microphone.finish()
        await dg_connection.finish()

    except Exception as e:
        print(f"Could not open socket: {e}")

class ConversationManager:
    def __init__(self):
        self.transcription_response = ""

    async def main(self):
        def handle_full_sentence(full_sentence):
            self.transcription_response = full_sentence

        while True:
            await get_transcript(handle_full_sentence)
            if "goodbye" in self.transcription_response.lower():
                break
            
            llm_response = conversation.invoke({"text": self.transcription_response})
            print(f"LLM Response: {llm_response['text']}")

            # Speak the response using Deepgram TTS
            self.speak(llm_response['text'])

            # Reset transcription response for the next loop iteration
            self.transcription_response = ""

    def speak(self, text):
        DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text
        }

        player_command = ["ffplay", "-autoexit", "-", "-nodisp"]
        player_process = subprocess.Popen(
            player_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        with requests.post(DEEPGRAM_URL, stream=True, headers=headers, json=payload) as r:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    player_process.stdin.write(chunk)
                    player_process.stdin.flush()

        player_process.stdin.close()
        player_process.wait()

if __name__ == "__main__":
    manager = ConversationManager()
    asyncio.run(manager.main())
