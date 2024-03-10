import assemblyai as aai
from openai import OpenAI
import elevenlabs
from queue import Queue

# Set API keys
aai.settings.api_key = "3550f42c1b2f41d1ab6027666b9ce6d7"
api_key = "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"
client = OpenAI(api_key = api_key)
elevenlabs.set_api_key("4e0f2a69188f25172725c65b23e2286a") 

transcript_queue = Queue()

def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        transcript_queue.put(transcript.text + '')
        print("User:", transcript.text, end="\r\n")
    else:
        print(transcript.text, end="\r")

def on_error(error: aai.RealtimeError):
    print("An error occured:", error)

# Conversation loop
def handle_conversation():
    while True:
        transcriber = aai.RealtimeTranscriber(
            on_data=on_data,
            on_error=on_error,
            sample_rate=44_100,
        )

        # Start the connection
        transcriber.connect()

        # Open  the microphone stream
        microphone_stream = aai.extras.MicrophoneStream()

        # Stream audio from the microphone
        transcriber.stream(microphone_stream)

        # Close current transcription session with Crtl + C
        transcriber.close()

        # Retrieve data from queue
        transcript_result = transcript_queue.get()

        # Send the transcript to OpenAI for response generation
        response = client.chat.completions.create(
            model = 'gpt-4',
            messages = [
                {"role": "system", "content": 'You are a highly skilled AI, answer the questions given within a maximum of 1000 characters.'},
                {"role": "user", "content": transcript_result}
            ]
        )

        text = response.choices[0].message.content
        #text = "AssemblyAI is the best YouTube channel for the latest AI tutorials."

        # Convert the response to audio and play it
        audio = elevenlabs.generate(
            text=text,
        )

        print("\nAI:", text, end="\r\n")

        elevenlabs.play(audio)

handle_conversation()