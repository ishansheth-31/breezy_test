from openai import OpenAI
import os
from pymongo import MongoClient
import re

api_key = os.getenv('OPENAI_API_KEY')
clientAI = OpenAI(api_key=api_key)

clientDB = MongoClient('mongodb+srv://ishansheth31:Kevi5han1234@breezytest1.saw2kxe.mongodb.net/')

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

    - Possible imaging tests or referral to physical therapy may be considered based on the assessment.
    Implementation:
    - Advised the patient on the importance of consulting a healthcare provider
    - Discussed the potential need for further diagnostic tests or physical therapy.
    Evaluation: 
    - To be determined based on patient's follow-up with healthcare provider and any subsequent treatment.

    Make sure to include the implementation and evaluation.

    Here is the chat history to base this off of below: \n"""

db = clientDB['breezydata']  # 
collection = db['emfd']  # 
db1 = clientDB['breezyassessements']  # 
collection1 = db1['emfd']  #

def create_report(assessment):
    # Your existing code to build the prompt and call OpenAI API...

    try:
        # Assuming the OpenAI response structure, adjust accordingly
        response = clientAI.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": new_prompt}]
        )
        # Ensure the text is extracted correctly from the response
        generated_text = response.choices[0].message.content  # Adjust based on actual response structure
        return generated_text
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return ""

# Then, when using the function:
for patient in collection.find({}):
    assessment = patient.get("Assessment")
    if not assessment or len(patient) <= 8:
        continue

    generated_text = create_report(assessment)
    if not isinstance(generated_text, str) or not generated_text.strip():
        print("Invalid or empty response for patient:", patient["_id"])
        continue

    # Your existing code for regex extraction and database insertion...


for patient in collection.find({}):
    assessment = patient.get("Assessment")
    if not assessment or len(patient) <= 8:
        continue

    generated_text = create_report(assessment)

    # Define regex patterns for each section
    section_patterns = {
        "Subjective": r"Subjective:(.*?)\n(?=Objective:)",
        "Objective": r"Objective:(.*?)\n(?=Analysis:)",
        "Analysis": r"Analysis:(.*?)\n(?=Plan:)",
        "Plan": r"Plan:(.*?)\n(?=Implementation:)",
        "Implementation": r"Implementation:(.*?)\n(?=Evaluation:)",
        "Evaluation": r"Evaluation:(.*)"
    }

    # Extract each section using the defined patterns
    extracted_sections = {section: re.search(pattern, generated_text, re.DOTALL).group(1).strip()
                          for section, pattern in section_patterns.items() if re.search(pattern, generated_text, re.DOTALL)}

    # Ensure all sections are found; otherwise, skip to the next patient
    if len(extracted_sections) != len(section_patterns):
        print("Not all sections were found for patient:", patient["_id"])
        continue

    # Insert the extracted sections into the MongoDB collection as a single document
    document_id = collection1.insert_one(extracted_sections)
    print(f"Inserted document ID: {document_id}")