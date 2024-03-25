import streamlit as st
from app import MedicalChatbot
from pymongo import MongoClient
from uuid import UUID
import os

mongo_key = os.getenv('MONGO_KEY')
client = MongoClient('mongodb+srv://ishansheth31:Kevi5han1234@breezytest1.saw2kxe.mongodb.net/')

db = client.EastMariettaFamilyDentistry
patients_collection = db.emfd

def initialize_session_state():
    if 'bot' not in st.session_state:
        st.session_state['bot'] = MedicalChatbot()
        st.session_state['chat_history'] = []
        st.session_state['initial_questions'] = [
            "Are you a new patient?",
            "What is your name?",
            "What is your approximate height in inches?",
            "What is your approximate weight in pounds?",
            "Are you currently taking any medications?",
            "Have you had any recent surgeries?",
            "Do you have any known drug allergies?",
            "Finally, what are you in for today?"
        ]
        st.session_state['initial_answers'] = {}
        st.session_state['current_question_index'] = 0

# Ensure initialization happens early in the app's execution
initialize_session_state()

# Now, you can safely access st.session_state.bot without encountering an AttributeError
if 'bot' in st.session_state:
    bot = st.session_state.bot
    # Proceed with the rest of your app logic here
else:
    st.error("Session state is not initialized correctly.")


def store_full_assessment_in_mongodb(chat_history, patient_id, patients_collection):
    # Extract answers from initial_questions and map them to the database columns
    answers = st.session_state['initial_answers']
    structured_data = {
        "New_Patient": answers.get("Are you a new patient?", "No information"),
        "Name": answers.get("What is your name?", "No information"),
        "Approx_Height": answers.get("What is your approximate height in inches?", "No information"),
        "Approx_Weight": answers.get("What is your approximate weight in pounds?", "No information"),
        "Medications": answers.get("Are you currently taking any medications?", "No information"),
        "Surgeries": answers.get("Have you had any recent surgeries?", "No information"),
        "Drug_Allergies": answers.get("Do you have any known drug allergies?", "No information"),
        "Reason_For_Visit": answers.get("Finally, what are you in for today?", "No information"),
        "Assessment": chat_history  # Store the full chat history in the Assessment field
    }

    # Update MongoDB with the structured data
    result = patients_collection.find_one_and_update(
        {"PatientID": patient_id},
        {"$set": structured_data},
        upsert=True,  # This will insert a new document if one doesn't exist
        return_document=True
    )

    if result:
        st.success("Assessment complete. We look forward to hearing from you soon!")
        return True
    else:
        st.error("Could not store the assessment. An error occurred.")
        return False



# Initialize the chatbot in the session state if it doesn't exist
if 'bot' not in st.session_state:
    st.session_state['bot'] = MedicalChatbot()
    st.session_state['chat_history'] = []
    st.session_state['initial_questions'] = [
        "Are you a new patient?",
        "What is your name?",
        "What is your approximate height in inches?",
        "What is your approximate weight in pounds?",
        "Are you currently taking any medications?",
        "Have you had any recent surgeries?",
        "Do you have any known drug allergies?",
        "Finally, what are you in for today?"
    ]
    st.session_state['initial_answers'] = {}
    st.session_state['current_question_index'] = 0

bot = st.session_state.bot

def display_chat_history():
    chat_container = st.container()
    with chat_container:
        for role, message in st.session_state.chat_history:
            if role == "You":
                st.markdown(f"**{role}:** {message}")
            else:
                st.markdown(f"*{role}:* {message}")

def handle_initial_questions():
    if st.session_state['current_question_index'] < len(st.session_state['initial_questions']):
        question = st.session_state['initial_questions'][st.session_state['current_question_index']]
        input_key = f"user_response_{st.session_state['current_question_index']}"
        detail_input_key = f"detail_{input_key}"

        user_response = None
        user_detail_response = None
        valid_response = False  # Track whether the response is valid

        if question in ["Are you a new patient?", "Are you currently taking any medications?", "Have you had any recent surgeries?", "Do you have any known drug allergies?"]:
            user_response = st.radio(question, ["Yes", "No"], key=input_key)
            valid_response = True  # Radio buttons always have a valid response
            if user_response == "Yes" and question in ["Are you currently taking any medications?", "Have you had any recent surgeries?", "Do you have any known drug allergies?"]:
                user_detail_response = st.text_input("Please elaborate", key=detail_input_key)
                valid_response = user_detail_response.strip() != ""  # Validate elaboration is not empty
        elif question == "What is your name?" or question == "Finally, what are you in for today?":
            user_response = st.text_input(question, key=input_key)
            valid_response = user_response.strip() != ""  # Validate name or reason is not empty
        elif question == "What is your approximate height in inches?":
            feet_key = f"{input_key}_feet"
            inches_key = f"{input_key}_inches"
            min_value_feet = 0 if feet_key in question.lower() else 0
            min_value_inches = 0 if inches_key in question.lower() else 0
            feet = st.number_input("Enter your Height: Feet", min_value=0, max_value=8, step=1, key=feet_key)
            inches = st.number_input("Inches", min_value=0, max_value=11, step=1, key=inches_key)
            user_response = f"{feet}' {inches}\""
            total_inches = feet * 12 + inches
            valid_response = feet >= min_value_feet and inches >= min_value_inches
        elif question in ["What is your approximate weight in pounds?"]:
            min_value = 0 if "weight" in question.lower() else 0  # Example minimum values for height and weight
            user_response = st.number_input(question, min_value=min_value, format="%d", key=input_key)
            valid_response = user_response >= min_value  # Validate height or weight is above minimum

        if st.button("Submit", key=f"submit_{input_key}"):
            if valid_response:
                st.session_state.chat_history.append(("Virtual Nurse", question))
                st.session_state.chat_history.append(("You", user_response))
                st.session_state.initial_answers[question] = user_response

                # If elaboration is required, save the answer
                if user_response == "Yes" and question in ["Are you currently taking any medications?", "Have you had any recent surgeries?", "Do you have any known drug allergies?"]:
                    elaboration_question = "Please elaborate"
                    st.session_state.chat_history.append(("Virtual Nurse", elaboration_question))
                    st.session_state.chat_history.append(("You", st.session_state.get(detail_input_key, "Not specified")))
                    st.session_state.initial_answers[elaboration_question] = st.session_state.get(detail_input_key, "Not specified")

                st.session_state['current_question_index'] += 1

                # If the last initial question was just answered, automatically generate a follow-up question from the LLM
                if question == "Finally, what are you in for today?":
                    follow_up_question = bot.generate_response(user_response)
                    st.session_state.chat_history.append(("Virtual Nurse", follow_up_question))
                    st.session_state['message_counter'] = 0  # Reset message counter for the next part of the conversation

                st.experimental_rerun()
            
            else:
                st.warning("Please provide a valid response.")

def extract_query_parameters():
    query_params = st.experimental_get_query_params()
    patient_id = query_params.get("patient_id", [None])[0]
    if patient_id is not None:
        try:
            # Validate that the patient_id is a valid UUID
            valid_uuid = UUID(patient_id, version=4)
            return str(valid_uuid)  # Return the validated UUID as a string
        except ValueError:
            return None
    return None


def handle_chat_after_initial_questions():
    if 'message_counter' not in st.session_state:
        st.session_state['message_counter'] = 0

    if not bot.finished:
        user_message_key = f"user_message_{st.session_state['message_counter']}"
        user_message = st.text_input("Your message:", key=user_message_key)

        if st.button("Send", key=f"send_{user_message_key}") and user_message:
            response = bot.generate_response(user_message)
            bot.should_stop(response)  # Check if the conversation should be stopped

            st.session_state.chat_history.append(("You", user_message))
            st.session_state.chat_history.append(("Virtual Nurse", response))
            
            st.session_state['message_counter'] += 1

            if bot.finished:
                st.success("Thank you for your time, we'll see you in the office later today.")
            else:
                st.experimental_rerun()






st.title("Virtual Nurse Patient Assessment")

url = "https://docs.google.com/document/d/1g63YfenbIJZXq9SG3l4kAcpLe9EOq126SGduGT4U5l4/edit?usp=sharing"

st.markdown("I consent to filling out this assessment. Click here to access our [document](%s) containing more information." % url)
if st.checkbox("Click here to accept"):

    display_chat_history()

    if st.session_state['current_question_index'] < len(st.session_state['initial_questions']):
        handle_initial_questions()
    else:
        handle_chat_after_initial_questions()

    patient_id = extract_query_parameters()


    if bot.finished == True:
        full_chat_history = st.session_state.chat_history
        
        patient_id = extract_query_parameters()  # Ensure this function returns the patient_id correctly
        if patient_id:
            store_full_assessment_in_mongodb(full_chat_history, patient_id, patients_collection)
        else:
            st.error("Could not update patient record. Patient ID is missing or invalid.")