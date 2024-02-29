#Physician portal
import streamlit as st
import pandas as pd
from pymongo import MongoClient

clientDB = MongoClient('mongodb+srv://ishansheth31:Kevi5han1234@breezytest1.saw2kxe.mongodb.net/')
db = clientDB['breezydata']  # 
collection = db['emfd']  # 

patients = collection.find({})  # This fetches all documents in the collection
db1 = clientDB['breezyassessements']  # 
collection1 = db1['emfd']





def physicianPortlal():
    st.title("Breezy Portal")
    st.write("---")
    st.subheader("**Today's Patients**")
physicianPortlal()

def sidebar():
    st.sidebar.header("Pending Patient Assesments...")
    st.sidebar.write("Patient5")
    st.sidebar.write("Patient6")
sidebar()

def patientAssesments():
    for patient in patients:
    # Create an expander for each patient
        with st.expander(f"{patient['fName']} {patient['lName']}"):
        
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.write(patient['fName'])
            col2.write(patient['lName'])
            col3.write("New Patient:{}".format(patient['New_Patient']))
            col4.write("**New Patient: No**")
            col5.write("Status:{}".format(patient["Status"]))
            tab1, tab2, tab3, tab4, tab6, tab5  = st.tabs(["Current Medications", "Tobacco History", "Allergies", "Surgical History", "Vitals", "Breezy Assesment"])
            #Current Meds
            tab1.write(patient['Medications'])
            #Tobacco
            #tab2.write(patient['Smoke'])
           # tab2.write(patient['second_smoke'])
            #allergies
            tab3.write(patient['Drug_Allergies'])
            #surgical
            tab4.write(patient['Surgeries'])
            #vitals
            tab6.write(patient['Approx_Height'])
            tab6.write(patient['Approx_Weight'])

            pAs = collection1.find({})
            for pA in pAs:
                   
                with tab5:
                    with st.container(height=200):
                        st.subheader("Subjective:")
                        st.markdown(pA["Subjective"])
                    with st.container(height=200):
                        st.subheader("Objective:")
                        st.markdown(pA["Objective"])
                    with st.container(height=200):
                        st.subheader("Assessement:")
                        st.markdown(pA["Analysis"])
                    with st.container(height=200):
                        st.subheader("Plan:")
                        st.markdown(pA["Plan"])
                    with st.container(height=200):
                        st.subheader("Implementation:")
                        st.markdown(pA["Implementation"])
                    with st.container(height=200):
                        st.subheader("Evaluation:")
                        st.markdown(pA["Evaluation"])    

        




















#     expander = st.expander("Patient1")
#     expander1 = st.expander("Patient2")
#     expander2 = st.expander("Patient3")
#     expander3 = st.expander("Patient4")
#     expander4 = st.expander("Patient5")

# #Creating a patient1 dropdown to view basic info 
#     with expander:
#         col1, col2, col3, col4 = st.columns(4)
#         col1.write(Info.firstname1)
#         col2.write(Info.lastname1)
#         col3.write(Info.birthday1)
#         col4.write("**New Patient: No**")

#         tab1, tab2, tab3, tab4, tab6, tab5  = st.tabs(["Current Medications", "Tobacco History", "Allergies", "Surgical History", "Vitals", "Breezy Assesment"])
#         #Current Meds
#         tab1.write(Info.medications1)
#         #Tobacco
#         tab2.write(Info.historysmoking1)
#         tab2.write(Info.secondhandsmoke1)
#         #allergies
#         tab3.write(Info.allergies1)
#         #surgical
#         tab4.write(Info.surgicalhistory1)
#         #vitals
#         tab6.write("Height:")
#         tab6.write("Weight:")
                   
#         with tab5:
#             with st.container(height=100):
#                 st.subheader("Subjective:")
#                 st.markdown("This is inside the contain")
#             with st.container(height=100):
#                 st.subheader("Objective:")
#                 st.markdown("This is inside the container")
#             with st.container(height=100):
#                 st.subheader("Assessement:")
#                 st.markdown("This is inside the container")
#             with st.container(height=100):
#                 st.subheader("Plan:")
#                 st.markdown("This is inside the container")
#             with st.container(height=100):
#                 st.subheader("Implementation:")
#                 st.markdown("This is inside the container")
#             with st.container(height=100):
#                 st.subheader("Evaluation:")
#                 st.markdown("This is inside the container")    
    
#     with expander1:
#             col1, col2, col3, col4 = st.columns(4)
#             col1.write(Info.firstname1)
#             col2.write(Info.lastname1)
#             col3.write(Info.birthday1)
#             col4.write("**New Patient: No**")

#             tab1, tab2, tab3, tab4, tab6, tab5  = st.tabs(["Current Medications", "Tobacco History", "Allergies", "Surgical History", "Vitals", "Breezy Assesment"])
#             #Current Meds
#             tab1.write(Info.medications1)
#             #Tobacco
#             tab2.write(Info.historysmoking1)
#             tab2.write(Info.secondhandsmoke1)
#             #allergies
#             tab3.write(Info.allergies1)
#             #surgical
#             tab4.write(Info.surgicalhistory1)
#             #vitals
#             tab6.write("Height:")
#             tab6.write("Weight:")
                    
#             with tab5:
#                 with st.container(height=100):
#                     st.subheader("Subjective:")
#                     st.markdown("This is inside the contain")
#                 with st.container(height=100):
#                     st.subheader("Objective:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Assessement:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Plan:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Implementation:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Evaluation:")
#                     st.markdown("This is inside the container")    
#     with expander2:
#             col1, col2, col3, col4 = st.columns(4)
#             col1.write(Info.firstname1)
#             col2.write(Info.lastname1)
#             col3.write(Info.birthday1)
#             col4.write("**New Patient: No**")

#             tab1, tab2, tab3, tab4, tab6, tab5  = st.tabs(["Current Medications", "Tobacco History", "Allergies", "Surgical History", "Vitals", "Breezy Assesment"])
#             #Current Meds
#             tab1.write(Info.medications1)
#             #Tobacco
#             tab2.write(Info.historysmoking1)
#             tab2.write(Info.secondhandsmoke1)
#             #allergies
#             tab3.write(Info.allergies1)
#             #surgical
#             tab4.write(Info.surgicalhistory1)
#             #vitals
#             tab6.write("Height:")
#             tab6.write("Weight:")
                    
#             with tab5:
#                 with st.container(height=100):
#                     st.subheader("Subjective:")
#                     st.markdown("This is inside the contain")
#                 with st.container(height=100):
#                     st.subheader("Objective:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Assessement:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Plan:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Implementation:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Evaluation:")
#                     st.markdown("This is inside the container")    
#     with expander3:
#         col1, col2, col3, col4 = st.columns(4)
#         col1.write(Info.firstname1)
#         col2.write(Info.lastname1)
#         col3.write(Info.birthday1)
#         col4.write("**New Patient: No**")

#         tab1, tab2, tab3, tab4, tab6, tab5  = st.tabs(["Current Medications", "Tobacco History", "Allergies", "Surgical History", "Vitals", "Breezy Assesment"])
#         #Current Meds
#         tab1.write(Info.medications1)
#         #Tobacco
#         tab2.write(Info.historysmoking1)
#         tab2.write(Info.secondhandsmoke1)
#         #allergies
#         tab3.write(Info.allergies1)
#         #surgical
#         tab4.write(Info.surgicalhistory1)
#         #vitals
#         tab6.write("Height:")
#         tab6.write("Weight:")
                
#         with tab5:
#             with st.container(height=100):
#                 st.subheader("Subjective:")
#                 st.markdown("This is inside the contain")
#             with st.container(height=100):
#                 st.subheader("Objective:")
#                 st.markdown("This is inside the container")
#             with st.container(height=100):
#                 st.subheader("Assessement:")
#                 st.markdown("This is inside the container")
#             with st.container(height=100):
#                 st.subheader("Plan:")
#                 st.markdown("This is inside the container")
#             with st.container(height=100):
#                 st.subheader("Implementation:")
#                 st.markdown("This is inside the container")
#             with st.container(height=100):
#                 st.subheader("Evaluation:")
#                 st.markdown("This is inside the container")    

#     with expander4:
#             col1, col2, col3, col4 = st.columns(4)
#             col1.write(Info.firstname1)
#             col2.write(Info.lastname1)
#             col3.write(Info.birthday1)
#             col4.write("**New Patient: No**")

#             tab1, tab2, tab3, tab4, tab6, tab5  = st.tabs(["Current Medications", "Tobacco History", "Allergies", "Surgical History", "Vitals", "Breezy Assesment"])
#             #Current Meds
#             tab1.write(Info.medications1)
#             #Tobacco
#             tab2.write(Info.historysmoking1)
#             tab2.write(Info.secondhandsmoke1)
#             #allergies
#             tab3.write(Info.allergies1)
#             #surgical
#             tab4.write(Info.surgicalhistory1)
#             #vitals
#             tab6.write("Height:")
#             tab6.write("Weight:")
                    
#             with tab5:
#                 with st.container(height=100):
#                     st.subheader("Subjective:")
#                     st.markdown("This is inside the contain")
#                 with st.container(height=100):
#                     st.subheader("Objective:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Assessement:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Plan:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Implementation:")
#                     st.markdown("This is inside the container")
#                 with st.container(height=100):
#                     st.subheader("Evaluation:")
#                     st.markdown("This is inside the container")    
patientAssesments()