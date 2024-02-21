import streamlit as st
import pandas as pd
from pymongo import MongoClient
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4
from gridfs import GridFS
import base64
from bson.binary import Binary
from docx import Document
from io import BytesIO
from openai import OpenAI
import os

new_prompt = """\nPHASE 3- Documentation Synthesis:
Document the patient's responses and any additional relevant information, as a nurse would for a doctor to use.

*rules*
-You have examples of what a nurses notes look like. Follow the 'SOAP' model for writing notes, you also have access to this in your knowledge.
-You should be very careful filling the O-Objective part of the note as most times you will not have the information to fill this out.
-Keep the notes easy and quick to read for a doctor. Ensure the notes get created in a Microsoft word document.
-You MUST use your knowledge of how to write good nursing notes and nursing note examples to format your notes properly.
-You MUST create a word document of the notes to deliver your final notes.
- You MUST use BULLET POINTS to allow for quick reading by doctor. They should not be repetitive
- For the implementation tab, you MUST not talk about communicating to a healthcare provider because they are visiting a doctor already

Here is an example document:

Subjective: 
- Patient reports a dull ache in the left shoulder, which started about a month ago
- The pain intensifies during workouts, especially during bench press. No previous injuries reported.
- No swelling, redness, or warmth in the area. Patient mentions a clicking sound when raising the arm laterally.
Objective: 
- Patient has been using ice and ibuprofen for pain management. 
- Ibuprofen provides temporary relief, and is needed approximately twice a day.
Analysis: 
- The symptoms suggest a potential joint issue in the left shoulder, possibly related to exercise. 
- The clicking sound during movement may indicate a ligament or tendon problem.
Plan: 
- Recommend patient to consult a healthcare provider for a physical examination. 
- Possible imaging tests or referral to physical therapy may be considered based on the assessment.
Implementation:
- Advised the patient on the importance of consulting a healthcare provider
- Discussed the potential need for further diagnostic tests or physical therapy.
Evaluation: 
- To be determined based on patient's follow-up with healthcare provider and any subsequent treatment.

Make sure to include the implementation and evaluation.

Here is the chat history to base this off of below: \n"""

api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=api_key)

# MongoDB setup
client = MongoClient("mongodb+srv://ishansheth31:Kevi5han1234@breezytest1.saw2kxe.mongodb.net/?retryWrites=true&w=majority")
db = client.breezydata
patients_collection = db.patientportal

def send_email(to_email, link):

    patient_id = str(uuid4())
    # Modify the link to include the patient ID as a query parameter
    personalized_link = f"{link}?patient_id={patient_id}"
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = 'mainbreezy11@gmail.com'
    smtp_password = 'qgzp kaay irpm hqyq'
    from_email = smtp_username
    subject = "Your Virtual Nurse Assessment"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    body = f"Please complete your assessment using the following link: {personalized_link}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        # Update patient status in MongoDB
        patients_collection.update_one({"Email": to_email}, {"$set": {"PatientID": patient_id, "Status": "Sent"}})
        return True
    except Exception as e:
        st.error(f"Failed to send email to {to_email}: {e}")
        return False

def fetch_patients():
    patients_list = list(patients_collection.find({}))
    patients_df = pd.DataFrame(patients_list)
    patients_df['Date'] = pd.to_datetime(patients_df['Date'])
    return patients_df

def generate_patient_assessment_report(patient_id):
    document = patients_collection.find_one({"PatientID": patient_id})
    if not document:
        return "No document found with PatientID: " + patient_id

    assessment = document.get('Assessment', None)
    if not assessment:
        return "Assessment not found in document"

    # Correctly format the chat history for the prompt
    # Adjusting to correctly handle the list of lists structure
    formatted_chat_history = "\n".join([f'{entry[0]}: "{entry[1]}"' for entry in assessment])

    basic_info = {
        "New Patient": document.get("New_Patient", "No information"),
        "Name": document.get("Name", "No information"),
        "Approx Height": document.get("Approx_Height", "No information"),
        "Approx Weight": document.get("Approx_Weight", "No information"),
        "Drug Allergies": document.get("Drug_Allergies", "No information"),
        "Medications": document.get("Medications", "No information"),
        "Surgeries": document.get("Surgeries", "No information"),
        "Reason For Visit": document.get("Reason_For_Visit", "No information"),
    }

    # Build the prompt for the report
    prompt = f"{new_prompt}\n\n{formatted_chat_history}"
    print(prompt)

    try:
        # Assuming 'response' is the variable holding the response from the OpenAI API call
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        # Correctly access the generated text from the response
        generated_report = response.choices[0].message.content  # Corrected way to access 'text'
        return generated_report, basic_info
    except Exception as e:
        return f"An error occurred: {str(e)}"



def download_report_as_word_document(basic_info, report_content, file_path='Patient_Assessment_Report.docx'):
    try:
        doc = Document()
        doc.add_heading('Patient Assessment Report', 0)

        # Add basic information
        doc.add_heading('Patient Information', level=1)
        for key, value in basic_info.items():
            doc.add_paragraph(f"{key}: {value}")

        doc.add_paragraph()  # Add a space between sections

        # Add the generated report content
        doc.add_heading('Assessment', level=1)
        doc.add_paragraph(report_content)

        doc.save(file_path)
        return file_path
    except Exception as e:
        return f"An error occurred: {str(e)}"

def display_patient_info():
    st.title("Breezy Portal")
    patients_df = fetch_patients()

    patients_df.sort_values(by='Date', inplace=True)
    patients_df['appointmentDate'] = patients_df['Date'].dt.date
    min_date = patients_df['appointmentDate'].min()
    max_date = patients_df['appointmentDate'].max()

    selected_date = st.sidebar.date_input("Select a Date", min_value=min_date, max_value=max_date, value=min_date)
    
    selected_patients = patients_df[patients_df['appointmentDate'] == selected_date]
    
    for _, patient in selected_patients.iterrows():
        appointment_time = patient['Date'].strftime('%I:%M %p')
        with st.expander(f"{patient['fName']} {patient['lName']} - {appointment_time}"):
            st.write(f"Email: {patient['Email']}")
            st.write(f"Status: {patient['Status']}")

            if patient['Status'] != "Sent":
                link = "https://breezy.streamlit.app"
                if st.button("Send Email", key=str(patient['_id'])):
                    if send_email(patient['Email'], link):
                        st.success(f"Email sent to {patient['Email']}")
                    else:
                        st.error("Failed to send email.")
            
            if patient['Status'] == "Sent":
                if st.button("Generate and Download Report", key=f"generate_{patient['_id']}"):
                    report_content, basic_info = generate_patient_assessment_report(patient["PatientID"])
                    file_path = download_report_as_word_document(basic_info, report_content)
                    st.success(f"Report generated: {file_path}")
                    # You may provide a direct link for downloading or use Streamlit's download button feature


def main():
    display_patient_info()

if __name__ == "__main__":
    main()