import streamlit as st
from app import MedicalChatbot

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

        # Initial response handling
        user_response = None
        if question in ["Are you a new patient?", "Are you currently taking any medications?", "Have you had any recent surgeries?", "Do you have any known drug allergies?"]:
            user_response = st.radio(question, ["Yes", "No"], key=input_key)
            if user_response == "Yes" and question in ["Are you currently taking any medications?", "Have you had any recent surgeries?", "Do you have any known drug allergies?"]:
                user_detail_response = st.text_input("Please elaborate", key=detail_input_key)
        elif question == "What is your name?" or question == "Finally, what are you in for today?":
            user_response = st.text_input(question, key=input_key)
        elif question in ["What is your approximate height in inches?", "What is your approximate weight in pounds?"]:
            unit = "inches" if "height" in question.lower() else "pounds"
            user_response = st.number_input(question, min_value=0, format="%d", key=input_key)
            user_response = f"{user_response} {unit}"

        if user_response is not None and st.button("Submit", key=f"submit_{input_key}"):
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

def handle_chat_after_initial_questions():
    if 'message_counter' not in st.session_state:
        st.session_state['message_counter'] = 0

    user_message_key = f"user_message_{st.session_state['message_counter']}"
    user_message = st.text_input("Your message:", key=user_message_key)
    submit_message = st.button("Send", key=f"send_{user_message_key}")

    if submit_message and user_message:
        response = bot.generate_response(user_message)
        st.session_state.chat_history.append(("You", user_message))
        st.session_state.chat_history.append(("Virtual Nurse", response))

        st.session_state['message_counter'] += 1

st.title("Virtual Nurse Patient Assessment")

display_chat_history()

if st.session_state['current_question_index'] < len(st.session_state['initial_questions']):
    handle_initial_questions()
else:
    handle_chat_after_initial_questions()

if st.button("Finish Conversation"):
    bot.finished = True
    for question, answer in st.session_state.initial_answers.items():
        bot.initial_questions_dict[question] = answer
    report_content = bot.create_report().choices[0].message.content
    file_path = bot.extract_and_save_report(report_content)
    st.write("### Patient Assessment Report")
    st.write(report_content)
    st.download_button("Download Report", data=open(file_path, "rb"), file_name="Patient_Assessment_Report.docx")