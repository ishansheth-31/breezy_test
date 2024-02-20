import streamlit as st
import pandas as pd
from pymongo import MongoClient
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4
from gridfs import GridFS
from io import BytesIO



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
    # Convert MongoDB query result to a pandas DataFrame for easier manipulation.
    patients_list = list(patients_collection.find({}))
    patients_df = pd.DataFrame(patients_list)
    # Convert 'Date' from string to datetime format for proper sorting
    patients_df['Date'] = pd.to_datetime(patients_df['Date'])
    return patients_df

def download_report(patient_id):
    fs = GridFS(db)
    patient = patients_collection.find_one({"PatientID": patient_id})
    if patient and "AssessmentFileID" in patient:
        grid_out = fs.get(patient['AssessmentFileID'])
        return grid_out.read(), grid_out.filename
    return None, None

def display_patient_info():
    display_patient_info()
    fs = GridFS(db)
    
    st.title("Breezy Portal")
    patients_df = fetch_patients()

    # Sort patients by 'Date' which now includes both date and time.
    patients_df.sort_values(by='Date', inplace=True)

    # Extract just the date part for the sidebar calendar.
    patients_df['appointmentDate'] = patients_df['Date'].dt.date
    min_date = patients_df['appointmentDate'].min()
    max_date = patients_df['appointmentDate'].max()

    # Use a calendar for date selection in the sidebar
    selected_date = st.sidebar.date_input("Select a Date", min_value=min_date, max_value=max_date, value=min_date)
    
    # Filter patients by the selected date.
    selected_patients = patients_df[patients_df['appointmentDate'] == selected_date]
    
    for _, patient in selected_patients.iterrows():
        # Format time to a 12-hour format with AM/PM.
        appointment_time = patient['Date'].strftime('%I:%M %p')
        patient_name_with_time = f"{patient['fName']} {patient['lName']} - {appointment_time}"
        with st.expander(patient_name_with_time):
            st.write(f"Email: {patient['Email']}")
            st.write(f"Status: {patient['Status']}")
            if patient['Assessment'] != "n/a":
                # Assuming 'Assessment' would be a valid URL or path to a document.
                st.markdown(f"[Download Assessment]({patient['Assessment']})")
            if st.button("Send Email", key=str(patient['_id'])):
                link = "https://breezy.streamlit.app"
                if send_email(patient['Email'], link):
                    st.success(f"Email sent to {patient['Email']}")
                else:
                    st.error("Failed to send email.")
            if 'Assessment' in patient:
                file_id = patient['Assessment']
                grid_out = fs.get(file_id)
                file_data = grid_out.read()
                file_name = grid_out.filename
                download_button_label = "Download Report"
                st.download_button(label=download_button_label, data=BytesIO(file_data), file_name=file_name, mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

def main():
    display_patient_info()

if __name__ == "__main__":
    main()