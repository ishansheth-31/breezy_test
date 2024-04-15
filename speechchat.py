import assemblyai as aai
from openai import OpenAI
from gtts import gTTS
from playsound import playsound
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import time
import os

# API Keys
aai_api_key = "f47fc69f44914e5d973f9d2f719ba271"
openai_api_key = "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"

# Initialize clients
aai.settings.api_key = aai_api_key
openai_client = OpenAI(api_key=openai_api_key)

class AI_Assistant:
    def __init__(self):
        self.openai_client = openai_client
        self.full_transcript = []

    def text_to_speech(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save('response.mp3')
        playsound('response.mp3')
        os.remove('response.mp3')

    def speech_to_text(self, audio_path):
        transcription = aai.Transcription(audio_path)
        transcript = transcription.get_result()
        return transcript['text']

    def handle_query(self, text):
        # OpenAI GPT prompt setup for medical assessment
        response = self.openai_client.Completion.create(
            model="gpt-3.5-turbo",
            prompt=f"You are a virtual nurse conducting a patient assessment. Let's get started: {text}",
            max_tokens=150
        )
        return response.choices[0].text

    def capture_speech(self, duration=5, samplerate=44100):
        print("Recording...")
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2)
        sd.wait()  # Wait until recording is finished
        write('output.wav', samplerate, recording)  # Save as WAV file
        return 'output.wav'

    def converse(self):
        while True:
            user_speech = self.capture_speech()
            user_text = self.speech_to_text(user_speech)
            self.full_transcript.append(user_text)
            print("You said:", user_text)
            
            response_text = self.handle_query(user_text)
            print("Assistant:", response_text)
            self.text_to_speech(response_text)
            self.full_transcript.append(response_text)

            if "exit" in user_text.lower():
                break

# To use the assistant
if __name__ == '__main__':
    assistant = AI_Assistant()
    assistant.converse()
