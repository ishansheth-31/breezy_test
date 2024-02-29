from openai import OpenAI
import os
from pymongo import MongoClient

clientAI = OpenAI(api_key="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")

clientDB = MongoClient('mongodb+srv://ishansheth31:Kevi5han1234@breezytest1.saw2kxe.mongodb.net/')

db = clientDB['breezydata']  # 
collection = db['emfd']  # 
db1 = clientDB['breezyassesments']  # 
collection1 = db1['emfd']  #

def create_report():
            chat_history = assessment 
            # Build the prompt for the report
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
            
            chat_history_string = str(assessment)
            # for i in range(len(chat_history)):
            #     if i%2 == False:
            #         nurse = chat_history[i][1]
            #     if i%2 == True:
            #         patient_message = chat_history[i][1]
                      
                      
             #   role = message['role'].capitalize()
             #   content = message['content'].replace('\n', ' ')  # Replace newlines with spaces
                #chat_history_string += f"{role}: {content}\n"
            
            new_prompt += chat_history_string
            
            try:
                # Call the OpenAI API to generate the report
                response =  clientAI.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role" : "system", "content" : new_prompt}]
                )
                return response
            except Exception as e:
                print(f"An error occurred {str(e)}")
                return ""

patients = collection.find({})

for patient in collection.find({}):
    assessment = patient["Assessment"]
    generated_text = create_report().choices[0].message.content

    # # Process the generated text to extract SOAP sections
    # sections = generated_text.split(": \n")  # Split by section headers assuming they are followed by a newline
    # print(sections)
    # # Assuming sections follow the order: Subjective, Objective, Assessment, Plan, Implementation, Evaluation
    # subjective = sections[1].split("\nObjective:")[0].strip()
    # objective = sections[2].split("\nAssessment:")[0].strip()
    # assessmentSOAP = sections[3].split("\nPlan:")[0].strip()
    # plan = sections[4].split("\nImplementation:")[0].strip()
    # implementation = sections[5].split("\nEvaluation:")[0].strip()
    # evaluation = sections[6] if len(sections) > 6 else ""
    # print(subjective)
    import re

    # Define regex patterns for each section. Adjust patterns as needed for consistency in your SOAP notes
    section_patterns = {
        "Subjective": r"Subjective:(.*?)\n(?=Objective:)",
        "Objective": r"Objective:(.*?)\n(?=Analysis:)",
        "Analysis": r"Analysis:(.*?)\n(?=Plan:)",
        "Plan": r"Plan:(.*?)\n(?=Implementation:)",
        "Implementation": r"Implementation:(.*?)\n(?=Evaluation:)",
        "Evaluation": r"Evaluation:(.*)"
    }

    # Initialize a dictionary to hold the extracted sections
    extracted_sections = {}

    # Extract each section using the defined patterns
    for section, pattern in section_patterns.items():
        match = re.search(pattern, generated_text, re.DOTALL)
        if match:
            extracted_sections[section] = match.group(1).strip()
        else:
            extracted_sections[section] = "Section not found"

    # Accessing individual sections
    subjective = extracted_sections["Subjective"]
    objective = extracted_sections["Objective"]
    assessmentSOAP = extracted_sections["Analysis"]
    plan = extracted_sections["Plan"]
    implementation = extracted_sections["Implementation"]
    evaluation = extracted_sections["Evaluation"]




    document = {
        "text_id": "subjective",  # Replace or generate a unique identifier as needed
        "content": subjective,

        "text_id": "objective",  # Replace or generate a unique identifier as needed
        "content": objective,

        "text_id": "assesement",  # Replace or generate a unique identifier as needed
        "content": assessmentSOAP,

        "text_id": "plan",  # Replace or generate a unique identifier as needed
        "content": plan,

        "text_id": "implementation",  # Replace or generate a unique identifier as needed
        "content": implementation,

        "text_id": "evaluation",  # Replace or generate a unique identifier as needed
        "content": evaluation
    }

    # Insert the document into the collection
    collection1.insert_one(document)
