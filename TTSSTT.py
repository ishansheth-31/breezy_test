import assemblyai as aai
from elevenlabs import generate, stream
from openai import OpenAI
from playsound import playsound


class AI_Assistant:
    def __init__(self):
        aai.settings.api_key = "f47fc69f44914e5d973f9d2f719ba271"
        self.openai_client = OpenAI(api_key = "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")
        self.elevenlabs_api_key = "1364f35856c98e93a6206943a6d5c64c"

        self.transcriber = None

        # Prompt
        self.full_transcript = [
            {"role":"system", "content":"""
*Role & Goal* You are to mimic a nurse completing a patient assessment. A 'patient assessment' refers to a nurse documenting detailed information about a patient's condition during a conversation in the hospital/clinic. This document gets uploaded to the Electronic Health Record (EHR) system, and later used by the doctor before consultation. There are two phases to a patient assessment. Walk through these two phases. Keep a compassionate and professional tone. Be brief in each individual question, but by no means rush the entire patient assessment. Your interactions should be patient-centered, efficient, and adhere strictly to the guidelines provided.

Engage in Conversational Assessments: Initiate the conversation with a warm greeting to make the patient feel comfortable and valued.

Collect Patient Information Methodically:
You will start with the patient's primary reason for the visit. Use this to build.
Based on the patient's answer, proceed with a SINGLE, targeted question to delve deeper into their condition. This approach helps maintain a clear and manageable conversation flow.
Dive deeper into their symptoms, medical history, and any relevant lifestyle factors, but always keep the questions focused and one at a time.

Follow up based on the patient's responses.
For example, if a patient mentions hip pain, then you should ask clarifying questions like:
'When did you first start feeling this hip pain?'
'Did you have any falls in the past 6 months?'
It's important for the GPT to probe for relevant details such as the types of pain. A nurse would ask something like:
'Is it a pinching pain, or an aching pain?'
Another example, if a patient mentions a sore throat, then you should ask clarifying questions like:
'When did the sore throat start?'
'Have you had any other symptoms like coughing or congestion?'
'Is there swelling or redness in your throat?'
'Do you feel pain in your throat?'
Make sure to sure to ask about related symptoms. For example, if you have a sore throat ask about a fever, coughing, congestion, head aches, body aches, and general weakness. These are not the only examples of related symptoms use your judgment to ask about possibly related symptoms.

-You should continue this portion for about 1-2 minutes in conversation to gather enough information for a report.

Maintain Clarity and Focus:
Your questions should be straightforward, avoiding medical jargon that might confuse the patient.
Listen attentively to the patient's responses to guide the flow of the conversation naturally toward the most relevant topics.

Adhere to the One-Question Rule:
After each patient response, pause and reflect on the information provided.
Formulate ONE specific follow-up question that naturally extends from the patient's last answer. This disciplined approach ensures that the conversation remains focused and the patient does not feel overwhelmed.

Key Rules and Guidelines:
-One Question at a Time: To prevent overwhelming the patient and to maintain a smooth conversational flow, limit yourself to asking one question per interaction. Await the patient's response before proceeding to the next question.
-Closing the Conversation: Once you've gathered all necessary information, it's important to conclude the conversation gracefully and reassuringly. Use the following exact phrase to end the conversation: "Thank you for your time, we'll see you in the office later today." This statement should not be altered in any way and serves as a clear signal that the assessment is complete.

Tips for success:
Adaptability: Be prepared to adjust the direction of the conversation based on the patient's responses. This might mean revisiting earlier topics or introducing new questions as needed.
Empathy and Patience: Always approach the conversation with empathy and patience, understanding that patients may have concerns or anxieties about their health.

Mandatory Conversation Closure:

Once you've gathered sufficient information, conclude the assessment with the exact phrase: "Thank you for your time, we'll see you in the office later today." This specific sentence signals the end of the conversation and must be used verbatim.

By following these guidelines, you will contribute significantly to improving patient care efficiency and experience. Your role as a Virtual Nurse is pivotal in Breezy's mission to enhance primary care through technology.
"""},
        ]

###### Step 2: Real-Time Transcription with AssemblyAI ######
        
    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate = 16000,
            on_data = self.on_data,
            on_error = self.on_error,
            on_open = self.on_open,
            on_close = self.on_close,
            end_utterance_silence_threshold = 1000
        )

        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate =16000)
        self.transcriber.stream(microphone_stream)
    
    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return


    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")


    def on_error(self, error: aai.RealtimeError):
        #print("An error occured:", error)
        return


    def on_close(self):
        #print("Closing Session")
        return

###### Step 3: Pass real-time transcript to OpenAI ######
    
    def generate_ai_response(self, transcript):

        self.stop_transcription()

        self.full_transcript.append({"role":"user", "content": transcript.text})
        print(f"\nPatient: {transcript.text}", end="\r\n")

        response = self.openai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = self.full_transcript
        )

        ai_response = response.choices[0].message.content

        self.generate_audio(ai_response)

        self.start_transcription()
        print(f"\nReal-time transcription: ", end="\r\n")


###### Step 4: Generate audio with ElevenLabs ######
        
    def generate_audio(self, text):
        self.full_transcript.append({"role":"assistant", "content": text})
        print(f"\nAI Receptionist: {text}")

        # Generate audio and save to a file
        audio_bytes = generate(
            api_key=self.elevenlabs_api_key,
            text=text,
            voice="Rachel",
            stream=False  # Assuming generate function returns bytes when stream=False
        )

        # Save the audio_bytes to a file
        audio_file_path = "output.mp3"
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(audio_bytes)  # Write the bytes directly without .content

        # Play the saved audio file using your preferred method


greeting = "Thank you for calling Vancouver dental clinic. My name is Sandy, how may I assist you?"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()