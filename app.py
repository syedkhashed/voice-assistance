import asyncio
import shutil
import subprocess
import requests
import time
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

# Replace with your actual API keys
DG_API_KEY = "9c5ccd2db18c95a12574e844e2137dd22d33c3e8"
GROQ_API_KEY = "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"

class LanguageModelProcessor:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768", groq_api_key=GROQ_API_KEY)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        system_prompt = """You are a conversational assistant named Eliza.
Use short, conversational responses as if you're having a live conversation.
Your response should be under 20 words.
Do not respond with any code, only conversation"""
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{text}")
        ])

        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory
        )

    def process(self, text):
        self.memory.chat_memory.add_user_message(text)
        response = self.conversation.invoke({"text": text})
        self.memory.chat_memory.add_ai_message(response['text'])
        return response['text']

class TextToSpeech:
    MODEL_NAME = "aura-helios-en"

    @staticmethod
    def is_installed(lib_name: str) -> bool:
        return shutil.which(lib_name) is not None

    def speak(self, text):
        if not self.is_installed("ffplay"):
            raise ValueError("ffplay not found, necessary to stream audio.")

        DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={self.MODEL_NAME}&performance=some&encoding=linear16&sample_rate=24000"
        headers = {
            "Authorization": f"Token {DG_API_KEY}",
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

async def get_transcript():
    transcription_complete = asyncio.Event()
    full_sentence = ""

    try:
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram = DeepgramClient(DG_API_KEY, config)

        dg_connection = deepgram.listen.asynclive.v("1")
        print("Listening...")

        async def on_message(result, **kwargs):
            nonlocal full_sentence
            sentence = result.channel.alternatives[0].transcript
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
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

        microphone = Microphone(dg_connection.send)
        microphone.start()

        await transcription_complete.wait()

        microphone.finish()
        await dg_connection.finish()

        return full_sentence

    except Exception as e:
        print(f"Could not open socket: {e}")
        return ""

class ConversationManager:
    def __init__(self):
        self.llm = LanguageModelProcessor()

    async def main(self):
        while st.session_state.is_listening:
            transcription_response = await get_transcript()
            if transcription_response and "goodbye" in transcription_response.lower():
                st.session_state.is_listening = False
                break
            
            st.session_state.transcription_response = transcription_response
            llm_response = self.llm.process(transcription_response)
            st.session_state.llm_response = llm_response

            tts = TextToSpeech()
            tts.speak(llm_response)

def run_streamlit_app():
    st.title("Voice Assistant")
    
    # Initialize session state variables
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False
    if 'transcription_response' not in st.session_state:
        st.session_state.transcription_response = ""
    if 'llm_response' not in st.session_state:
        st.session_state.llm_response = ""

    manager = ConversationManager()

    if st.button("Start Listening") and not st.session_state.is_listening:
        st.session_state.is_listening = True
        st.session_state.transcription_response = ""
        st.session_state.llm_response = ""
        st.write("Listening...")

        # Run the main loop in an async manner
        asyncio.run(manager.main())
    
    if st.button("Stop Listening") and st.session_state.is_listening:
        st.session_state.is_listening = False
        st.write("Stopped listening.")

    # Display the transcription and LLM responses
    if st.session_state.transcription_response:
        st.write(f"Input: {st.session_state.transcription_response}")

    if st.session_state.llm_response:
        st.write(f"Output: {st.session_state.llm_response}")

if __name__ == "__main__":
    run_streamlit_app()
