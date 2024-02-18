import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load patient data
def load_patient_data():
    patients_csv_path = 'patients.csv'  # Update this path accordingly
    return pd.read_csv(patients_csv_path, sep='\t')

def send_email(to_email, link):
    # Email setup (customize with your SMTP server details)
    smtp_server = "your.smtp.server.com"
    smtp_port = 587  # or 465 for SSL
    smtp_username = "your_username"
    smtp_password = "your_password"
    from_email = "your_email@example.com"
    subject = "Your Virtual Nurse Assessment"
    
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    body = f"Please complete your assessment using the following link: {link}"
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
    server.quit()

def display_patient_info(df, selected_date):
    st.title("Breezy Portal")
    st.write("---")
    st.subheader(f"**Patients for {selected_date.strftime('%Y-%m-%d')}**")
    
    # Filter patients by the selected date
    filtered_patients = df[df['Appointment Date'] == pd.to_datetime(selected_date)]
    if not filtered_patients.empty:
        # Sort by time for the selected date
        filtered_patients_sorted = filtered_patients.sort_values(by='Time')
        # Display as a table
        displayed_table = st.table(filtered_patients_sorted[['Patient Name', 'Email', 'Time', 'Status']])
        
        # Button to send email
        if st.button("Send Assessment Link"):
            for index, patient in filtered_patients_sorted.iterrows():
                send_email(patient['Email'], "http://link-to-virtual-nurse")
                st.success(f"Assessment link sent to {patient['Email']}!")
    else:
        st.write("No patients scheduled for this date.")

def sidebar(df):
    st.sidebar.header("Select Appointment Date")
    min_date = pd.to_datetime(df['Appointment Date']).min()
    max_date = pd.to_datetime(df['Appointment Date']).max()
    selected_date = st.sidebar.date_input("Date", min_value=min_date, max_value=max_date, value=min_date)
    
    return selected_date

def main():
    df = load_patient_data()
    # Convert 'Appointment Date' to datetime for filtering
    df['Appointment Date'] = pd.to_datetime(df['Appointment Date'])
    selected_date = sidebar(df)
    display_patient_info(df, selected_date)

if __name__ == "__main__":
    main()
